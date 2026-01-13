"""
Core RLM Implementation with Optimizations.

Optimizations included:
- Connection pooling (HTTP/2)
- Batched recursive calls
- Async support
- Streaming output
- Usage tracking
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import AsyncIterator, Callable, Literal

from .clients import create_client, BaseLLMClient, Backend
from .clients.base import LLMUsage
from .repl import PythonREPL, REPLResult
from .prompts import build_system_prompt, build_continuation_prompt
from .parser import extract_code_blocks, extract_final_answer, format_code_output


@dataclass
class RLMConfig:
    """Configuration for RLM."""
    max_iterations: int = 20
    max_depth: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096
    verbose: bool = True
    stream: bool = False


@dataclass
class RLMResult:
    """Result from RLM completion."""
    answer: str
    iterations: int
    total_llm_calls: int
    usage: LLMUsage = field(default_factory=LLMUsage)
    execution_time: float = 0.0
    success: bool = True
    error: str | None = None


class RLM:
    """
    Recursive Language Model - Process unlimited context via code execution.
    
    Works with:
    - OpenAI API (no deployment needed)
    - Anthropic API (no deployment needed)  
    - vLLM (self-hosted)
    - Ollama (local)
    
    Optimizations:
    - Connection pooling for reduced latency
    - Batched parallel recursive calls
    - Async support for better throughput
    - Streaming for real-time output
    
    Examples:
        # With OpenAI (easiest - just needs API key)
        rlm = RLM(backend="openai", model="gpt-4o-mini")
        
        # With self-hosted vLLM
        rlm = RLM(
            backend="vllm",
            model="meta-llama/Llama-3.1-8B-Instruct",
            base_url="http://localhost:8000/v1"
        )
        
        # Process document
        result = rlm.completion("Summarize this", context=huge_document)
    """
    
    def __init__(
        self,
        backend: Backend = "openai",
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        config: RLMConfig | None = None,
        **kwargs,
    ):
        """
        Initialize RLM.
        
        Args:
            backend: One of "openai", "anthropic", "vllm", "ollama"
            model: Model name (uses default for backend if not specified)
            base_url: API endpoint (required for vllm/ollama)
            api_key: API key (uses env var if not specified)
            config: RLM configuration
        """
        self.client = create_client(
            backend=backend,
            model=model,
            base_url=base_url,
            api_key=api_key,
            **kwargs,
        )
        self.backend = backend
        self.config = config or RLMConfig()
        
        # Statistics
        self._total_llm_calls = 0
        self._current_depth = 0
    
    def completion(
        self,
        query: str,
        context: str,
        callback: Callable[[str], None] | None = None,
    ) -> RLMResult:
        """
        Process a query over a context of any length.
        
        Args:
            query: The question/task to perform
            context: The document to analyze (can be 10M+ characters)
            callback: Optional callback for progress updates
            
        Returns:
            RLMResult with the answer
        """
        start_time = time.perf_counter()
        self._total_llm_calls = 0
        
        try:
            result = self._run_rlm(query, context, depth=0, callback=callback)
            result.execution_time = time.perf_counter() - start_time
            result.usage = self.client.usage
            return result
        except Exception as e:
            return RLMResult(
                answer="",
                iterations=0,
                total_llm_calls=self._total_llm_calls,
                execution_time=time.perf_counter() - start_time,
                success=False,
                error=str(e),
            )
    
    async def acompletion(
        self,
        query: str,
        context: str,
    ) -> RLMResult:
        """
        Async version of completion.
        """
        start_time = time.perf_counter()
        self._total_llm_calls = 0
        
        try:
            result = await self._arun_rlm(query, context, depth=0)
            result.execution_time = time.perf_counter() - start_time
            result.usage = self.client.usage
            return result
        except Exception as e:
            return RLMResult(
                answer="",
                iterations=0,
                total_llm_calls=self._total_llm_calls,
                execution_time=time.perf_counter() - start_time,
                success=False,
                error=str(e),
            )
    
    def _run_rlm(
        self,
        query: str,
        context: str,
        depth: int,
        callback: Callable[[str], None] | None = None,
    ) -> RLMResult:
        """Internal RLM loop (synchronous)."""
        
        if depth >= self.config.max_depth:
            return self._direct_completion(query, context)
        
        # Create recursive call functions
        def llm_query(sub_query: str) -> str:
            result = self._run_rlm(sub_query, context, depth + 1, callback)
            return result.answer
        
        def llm_query_batch(prompts: list[str]) -> list[str]:
            # Run batch synchronously using asyncio
            async def batch():
                tasks = [
                    self._arun_rlm(p, context, depth + 1)
                    for p in prompts
                ]
                results = await asyncio.gather(*tasks)
                return [r.answer for r in results]
            
            return asyncio.run(batch())
        
        # Create REPL environment
        repl = PythonREPL(
            context=context,
            llm_query_fn=llm_query,
            llm_query_batch_fn=llm_query_batch,
        )
        
        # Build initial messages
        system_prompt = build_system_prompt(len(context), depth)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        
        # Main loop
        for iteration in range(self.config.max_iterations):
            if self.config.verbose:
                self._log(f"\n{'='*50}")
                self._log(f"[Depth {depth}] Iteration {iteration + 1}/{self.config.max_iterations}")
            
            if callback:
                callback(f"Iteration {iteration + 1}")
            
            # Call LLM
            self._total_llm_calls += 1
            response = self.client.chat_completion(
                messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            llm_output = response.content
            
            if self.config.verbose:
                preview = llm_output[:300] + "..." if len(llm_output) > 300 else llm_output
                self._log(f"LLM ({response.model}):\n{preview}")
            
            # Check for FINAL answer
            final_answer = extract_final_answer(llm_output)
            if final_answer:
                if self.config.verbose:
                    self._log(f"\n✅ FINAL: {final_answer[:200]}...")
                return RLMResult(
                    answer=final_answer,
                    iterations=iteration + 1,
                    total_llm_calls=self._total_llm_calls,
                )
            
            # Extract and execute code blocks
            code_blocks = extract_code_blocks(llm_output)
            
            if code_blocks:
                outputs = []
                for code in code_blocks:
                    if self.config.verbose:
                        self._log(f"\n📝 Executing code:\n{code[:200]}...")
                    
                    result = repl.execute(code)
                    
                    # Check if FINAL() was called in the code
                    if result.final_answer:
                        if self.config.verbose:
                            self._log(f"\n✅ FINAL (from code): {result.final_answer[:200]}...")
                        return RLMResult(
                            answer=result.final_answer,
                            iterations=iteration + 1,
                            total_llm_calls=self._total_llm_calls,
                        )
                    
                    output = format_code_output(result.stdout, result.stderr)
                    outputs.append(output)
                    
                    if self.config.verbose:
                        self._log(f"📤 Output:\n{output[:300]}")
                
                # Add to conversation
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({"role": "user", "content": "\n---\n".join(outputs)})
            else:
                # No code blocks - prompt for code
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({
                    "role": "user",
                    "content": build_continuation_prompt(iteration + 1),
                })
        
        # Max iterations reached
        return RLMResult(
            answer="Max iterations reached without final answer",
            iterations=self.config.max_iterations,
            total_llm_calls=self._total_llm_calls,
            success=False,
            error="Max iterations exceeded",
        )
    
    async def _arun_rlm(
        self,
        query: str,
        context: str,
        depth: int,
    ) -> RLMResult:
        """Internal RLM loop (asynchronous)."""
        
        if depth >= self.config.max_depth:
            return await self._adirect_completion(query, context)
        
        # Create async recursive call functions
        async def llm_query_async(sub_query: str) -> str:
            result = await self._arun_rlm(sub_query, context, depth + 1)
            return result.answer
        
        def llm_query(sub_query: str) -> str:
            # Sync wrapper for REPL
            return asyncio.get_event_loop().run_until_complete(
                llm_query_async(sub_query)
            )
        
        async def llm_query_batch_async(prompts: list[str]) -> list[str]:
            # OPTIMIZATION: Run all in parallel
            tasks = [self._arun_rlm(p, context, depth + 1) for p in prompts]
            results = await asyncio.gather(*tasks)
            return [r.answer for r in results]
        
        def llm_query_batch(prompts: list[str]) -> list[str]:
            return asyncio.get_event_loop().run_until_complete(
                llm_query_batch_async(prompts)
            )
        
        # Create REPL environment
        repl = PythonREPL(
            context=context,
            llm_query_fn=llm_query,
            llm_query_batch_fn=llm_query_batch,
        )
        
        # Build initial messages
        system_prompt = build_system_prompt(len(context), depth)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        
        # Main loop
        for iteration in range(self.config.max_iterations):
            if self.config.verbose:
                self._log(f"[Depth {depth}] Iteration {iteration + 1}")
            
            # Call LLM (async)
            self._total_llm_calls += 1
            response = await self.client.achat_completion(
                messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            llm_output = response.content
            
            # Check for FINAL answer
            final_answer = extract_final_answer(llm_output)
            if final_answer:
                return RLMResult(
                    answer=final_answer,
                    iterations=iteration + 1,
                    total_llm_calls=self._total_llm_calls,
                )
            
            # Execute code blocks
            code_blocks = extract_code_blocks(llm_output)
            
            if code_blocks:
                outputs = []
                for code in code_blocks:
                    result = repl.execute(code)
                    
                    # Check if FINAL() was called in the code
                    if result.final_answer:
                        return RLMResult(
                            answer=result.final_answer,
                            iterations=iteration + 1,
                            total_llm_calls=self._total_llm_calls,
                        )
                    
                    output = format_code_output(result.stdout, result.stderr)
                    outputs.append(output)
                
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({"role": "user", "content": "\n---\n".join(outputs)})
            else:
                messages.append({"role": "assistant", "content": llm_output})
                messages.append({
                    "role": "user",
                    "content": build_continuation_prompt(iteration + 1),
                })
        
        return RLMResult(
            answer="Max iterations reached",
            iterations=self.config.max_iterations,
            total_llm_calls=self._total_llm_calls,
            success=False,
        )
    
    def _direct_completion(self, query: str, context: str) -> RLMResult:
        """Direct LLM call when at max depth."""
        max_ctx = 8000
        truncated = context[:max_ctx] if len(context) > max_ctx else context
        
        self._total_llm_calls += 1
        response = self.client.chat_completion([
            {"role": "user", "content": f"{query}\n\nContext:\n{truncated}"}
        ])
        
        return RLMResult(
            answer=response.content,
            iterations=1,
            total_llm_calls=self._total_llm_calls,
        )
    
    async def _adirect_completion(self, query: str, context: str) -> RLMResult:
        """Async direct LLM call when at max depth."""
        max_ctx = 8000
        truncated = context[:max_ctx] if len(context) > max_ctx else context
        
        self._total_llm_calls += 1
        response = await self.client.achat_completion([
            {"role": "user", "content": f"{query}\n\nContext:\n{truncated}"}
        ])
        
        return RLMResult(
            answer=response.content,
            iterations=1,
            total_llm_calls=self._total_llm_calls,
        )
    
    def _log(self, message: str):
        """Print log message if verbose."""
        if self.config.verbose:
            print(message)
    
    @property
    def usage(self) -> LLMUsage:
        """Get total token usage."""
        return self.client.usage
    
    @property
    def call_count(self) -> int:
        """Get total LLM API calls."""
        return self.client.call_count
    
    def close(self):
        """Clean up resources."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
