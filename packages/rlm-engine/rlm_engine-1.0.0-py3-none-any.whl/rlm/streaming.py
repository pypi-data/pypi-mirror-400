"""Streaming support for RLM."""
import asyncio
from typing import AsyncIterator, Callable, Optional
from dataclasses import dataclass

from .core import RLM, RLMConfig, RLMResult
from .repl import PythonREPL
from .prompts import build_system_prompt, build_continuation_prompt
from .parser import extract_code_blocks, extract_final_answer, format_code_output


@dataclass
class StreamEvent:
    """Event emitted during streaming."""
    event_type: str  # "iteration", "code", "output", "answer", "error"
    data: str
    iteration: int = 0
    
    def __str__(self):
        return f"[{self.event_type}] {self.data}"


class StreamingRLM:
    """
    RLM with streaming output.
    
    Yields events as the RLM progresses through iterations.
    """
    
    def __init__(self, rlm: RLM):
        self.rlm = rlm
        self.config = rlm.config
    
    async def stream_completion(
        self,
        query: str,
        context: str,
        on_event: Optional[Callable[[StreamEvent], None]] = None,
    ) -> AsyncIterator[StreamEvent]:
        """
        Stream RLM completion with events.
        
        Args:
            query: The question to answer
            context: The document to analyze
            on_event: Optional callback for each event
            
        Yields:
            StreamEvent objects for each step
        """
        self.rlm._total_llm_calls = 0
        
        def llm_query(sub_query: str) -> str:
            result = self.rlm._run_rlm(sub_query, context, depth=1)
            return result.answer
        
        def llm_query_batch(prompts: list[str]) -> list[str]:
            return [llm_query(p) for p in prompts]
        
        repl = PythonREPL(
            context=context,
            llm_query_fn=llm_query,
            llm_query_batch_fn=llm_query_batch,
        )
        
        system_prompt = build_system_prompt(len(context), depth=0)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        
        for iteration in range(self.config.max_iterations):
            # Emit iteration start
            event = StreamEvent(
                event_type="iteration",
                data=f"Starting iteration {iteration + 1}",
                iteration=iteration + 1,
            )
            if on_event:
                on_event(event)
            yield event
            
            # Call LLM
            self.rlm._total_llm_calls += 1
            response = self.rlm.client.chat_completion(
                messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            llm_output = response.content
            
            # Check for FINAL answer
            final_answer = extract_final_answer(llm_output)
            if final_answer:
                event = StreamEvent(
                    event_type="answer",
                    data=final_answer,
                    iteration=iteration + 1,
                )
                if on_event:
                    on_event(event)
                yield event
                return
            
            # Extract and execute code
            code_blocks = extract_code_blocks(llm_output)
            
            if code_blocks:
                for code in code_blocks:
                    # Emit code event
                    event = StreamEvent(
                        event_type="code",
                        data=code[:500],
                        iteration=iteration + 1,
                    )
                    if on_event:
                        on_event(event)
                    yield event
                    
                    # Execute code
                    result = repl.execute(code)
                    
                    # Check if FINAL was called
                    if result.final_answer:
                        event = StreamEvent(
                            event_type="answer",
                            data=result.final_answer,
                            iteration=iteration + 1,
                        )
                        if on_event:
                            on_event(event)
                        yield event
                        return
                    
                    # Emit output event
                    output = format_code_output(result.stdout, result.stderr)
                    event = StreamEvent(
                        event_type="output",
                        data=output[:500],
                        iteration=iteration + 1,
                    )
                    if on_event:
                        on_event(event)
                    yield event
                
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({"role": "user", "content": output})
            else:
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({
                    "role": "user",
                    "content": build_continuation_prompt(iteration + 1),
                })
        
        # Max iterations reached
        event = StreamEvent(
            event_type="error",
            data="Max iterations reached without answer",
            iteration=self.config.max_iterations,
        )
        if on_event:
            on_event(event)
        yield event


async def stream_to_console(rlm: RLM, query: str, context: str):
    """Stream RLM output to console."""
    streaming = StreamingRLM(rlm)
    
    async for event in streaming.stream_completion(query, context):
        if event.event_type == "iteration":
            print(f"\n{'='*50}")
            print(f"Iteration {event.iteration}")
            print('='*50)
        elif event.event_type == "code":
            print(f"\n📝 Code:\n{event.data}")
        elif event.event_type == "output":
            print(f"\n📤 Output:\n{event.data}")
        elif event.event_type == "answer":
            print(f"\n✅ Answer: {event.data}")
        elif event.event_type == "error":
            print(f"\n❌ Error: {event.data}")
