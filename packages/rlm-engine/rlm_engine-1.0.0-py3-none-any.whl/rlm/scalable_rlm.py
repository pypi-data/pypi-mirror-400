"""
Scalable RLM - Production-ready with optimizations.

Adds to base RLM:
- Response caching
- Request batching
- Smart chunking
- Parallel processing
- Connection pooling
"""

import asyncio
from typing import Optional, Callable

from dataclasses import dataclass, field
from .core import RLM, RLMResult, RLMConfig
from .clients import Backend
from .optimizations.caching import LLMCache
from .optimizations.chunking import smart_chunk, parallel_map_reduce, Chunk


@dataclass
class ScalableRLMResult(RLMResult):
    """Extended result with scalability metrics."""
    chunks_processed: int = 0
    cache_hits: int = 0
    parallel_calls: int = 0


class ScalableRLM(RLM):
    """
    Production-ready RLM with scalability optimizations.
    
    Additional features:
    - LLM response caching (saves tokens on repeated queries)
    - Parallel chunk processing for large documents
    - Adaptive chunking based on content complexity
    
    Usage:
        rlm = ScalableRLM(
            backend="vllm",
            base_url="http://localhost:8000/v1",
            enable_cache=True,
            max_concurrent=10,
        )
        
        result = await rlm.scalable_completion(
            query="Summarize this 10M character document",
            context=huge_document,
        )
    """
    
    def __init__(
        self,
        backend: Backend = "openai",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[RLMConfig] = None,
        enable_cache: bool = True,
        cache_size: int = 1000,
        cache_ttl: float = 3600,
        max_concurrent: int = 5,
        **kwargs,
    ):
        super().__init__(
            backend=backend,
            model=model,
            base_url=base_url,
            api_key=api_key,
            config=config,
            **kwargs,
        )
        
        # Caching
        self.enable_cache = enable_cache
        self._cache = LLMCache(max_size=cache_size, ttl_seconds=cache_ttl) if enable_cache else None
        
        # Concurrency
        self.max_concurrent = max_concurrent
    
    async def scalable_completion(
        self,
        query: str,
        context: str,
        chunk_size: int = 10000,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> RLMResult:
        """
        Process large documents with parallel chunking.
        
        Strategy:
        1. Split into chunks
        2. Process chunks in parallel with RLM
        3. Aggregate results
        
        Args:
            query: The question/task
            context: Document (any size)
            chunk_size: Size of each chunk
            progress_callback: Called with (completed, total)
        """
        # For smaller documents, use standard completion
        if len(context) <= chunk_size * 2:
            return await self.acompletion(query, context)
        
        # Split into chunks
        chunks = smart_chunk(context, target_size=chunk_size)
        total_chunks = len(chunks)
        completed = 0
        
        if progress_callback:
            progress_callback(0, total_chunks)
        
        # Define map function (process each chunk)
        async def process_chunk(chunk: Chunk) -> str:
            nonlocal completed
            
            chunk_query = f"""
{query}

Note: This is chunk {chunk.chunk_id + 1} of {total_chunks} 
(characters {chunk.start_idx:,} to {chunk.end_idx:,}).
Extract relevant information for the query.
"""
            result = await self.acompletion(chunk_query, chunk.text)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total_chunks)
            
            return result.answer
        
        # Define reduce function (combine results)
        async def combine_results(chunk_answers: list[str]) -> str:
            combined = "\n\n---\n\n".join([
                f"[Chunk {i+1}]\n{ans}" 
                for i, ans in enumerate(chunk_answers)
            ])
            
            synthesis_query = f"""
Original query: {query}

I've analyzed {len(chunk_answers)} chunks of the document. Here are the findings:

{combined}

Please synthesize these into a single coherent answer to the original query.
"""
            # Use a fresh context for synthesis
            result = await self.acompletion(synthesis_query, "")
            return result.answer
        
        # Run parallel map-reduce
        final_answer = await parallel_map_reduce(
            chunks=chunks,
            map_fn=process_chunk,
            reduce_fn=combine_results,
            max_concurrent=self.max_concurrent,
        )
        
        return RLMResult(
            answer=final_answer,
            iterations=completed,  # Chunks processed
            total_llm_calls=self._total_llm_calls,
            usage=self.usage,
            success=True,
        )
    
    def completion_with_cache(
        self,
        query: str,
        context: str,
    ) -> RLMResult:
        """
        Completion with response caching.
        
        If the same query+context was seen before, returns cached result.
        """
        if not self._cache:
            return self.completion(query, context)
        
        # Create cache key from query + context hash
        import hashlib
        context_hash = hashlib.sha256(context.encode()).hexdigest()[:16]
        cache_key = [{"role": "cache", "content": f"{query}|{context_hash}"}]
        
        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            return RLMResult(
                answer=cached,
                iterations=0,
                total_llm_calls=0,
                success=True,
            )
        
        # Run completion
        result = self.completion(query, context)
        
        # Cache result
        if result.success:
            self._cache.set(cache_key, result.answer, result.usage.total_tokens)
        
        return result
    
    @property
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        if not self._cache:
            return {"enabled": False}
        return {"enabled": True, **self._cache.stats}


async def benchmark_scalability(
    rlm: ScalableRLM,
    sizes: list[int] = [10_000, 100_000, 500_000, 1_000_000],
) -> dict:
    """
    Benchmark RLM scalability across different context sizes.
    
    Returns metrics for each size.
    """
    import time
    
    results = {}
    base_text = "This is sample text for scalability testing. " * 100
    
    for size in sizes:
        # Generate context of target size
        repeats = (size // len(base_text)) + 1
        context = (base_text * repeats)[:size]
        
        print(f"\n📏 Testing {size:,} characters...")
        
        start = time.perf_counter()
        result = await rlm.scalable_completion(
            query="What is the approximate length of this document?",
            context=context,
            progress_callback=lambda c, t: print(f"   Progress: {c}/{t}", end="\r"),
        )
        elapsed = time.perf_counter() - start
        
        results[size] = {
            "context_chars": size,
            "latency_seconds": elapsed,
            "success": result.success,
            "llm_calls": result.total_llm_calls,
            "tokens": result.usage.total_tokens if result.usage else 0,
            "chars_per_second": size / elapsed,
        }
        
        print(f"   ✅ {elapsed:.1f}s ({size/elapsed:,.0f} chars/sec)")
    
    return results
