"""
Smart Chunking and Parallel Map-Reduce for Large Documents.

Optimizes how RLM splits and processes large contexts.
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Callable, Awaitable


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    text: str
    start_idx: int
    end_idx: int
    chunk_id: int
    
    @property
    def size(self) -> int:
        return len(self.text)


def smart_chunk(
    text: str,
    target_size: int = 4000,
    overlap: int = 200,
    respect_boundaries: bool = True,
) -> list[Chunk]:
    """
    Split text into chunks intelligently.
    
    Features:
    - Respects paragraph/sentence boundaries
    - Configurable overlap for context continuity
    - Maintains chunk metadata for reconstruction
    
    Args:
        text: Full document text
        target_size: Target chunk size in characters
        overlap: Characters of overlap between chunks
        respect_boundaries: Try to split at natural boundaries
        
    Returns:
        List of Chunk objects
    """
    if len(text) <= target_size:
        return [Chunk(text=text, start_idx=0, end_idx=len(text), chunk_id=0)]
    
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(text):
        # Calculate end position
        end = min(start + target_size, len(text))
        
        if end < len(text) and respect_boundaries:
            # Try to find a good break point
            end = _find_break_point(text, start, end)
        
        chunk_text = text[start:end]
        chunks.append(Chunk(
            text=chunk_text,
            start_idx=start,
            end_idx=end,
            chunk_id=chunk_id,
        ))
        
        # Move start, accounting for overlap
        start = end - overlap if end < len(text) else end
        chunk_id += 1
    
    return chunks


def _find_break_point(text: str, start: int, end: int) -> int:
    """Find a natural break point (paragraph, sentence, word)."""
    search_start = max(start, end - 500)  # Look back up to 500 chars
    
    # Try paragraph break
    para_break = text.rfind("\n\n", search_start, end)
    if para_break > search_start:
        return para_break + 2
    
    # Try sentence break
    for pattern in [". ", "! ", "? ", ".\n"]:
        sent_break = text.rfind(pattern, search_start, end)
        if sent_break > search_start:
            return sent_break + len(pattern)
    
    # Try word break
    word_break = text.rfind(" ", search_start, end)
    if word_break > search_start:
        return word_break + 1
    
    return end


async def parallel_map_reduce(
    chunks: list[Chunk],
    map_fn: Callable[[Chunk], Awaitable[str]],
    reduce_fn: Callable[[list[str]], Awaitable[str]],
    max_concurrent: int = 5,
) -> str:
    """
    Process chunks in parallel and reduce results.
    
    This is the core scalability pattern for RLM:
    1. Split document into chunks
    2. Process chunks in parallel (map)
    3. Combine results (reduce)
    
    Args:
        chunks: List of document chunks
        map_fn: Async function to process each chunk
        reduce_fn: Async function to combine results
        max_concurrent: Maximum parallel operations
        
    Returns:
        Final reduced result
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_map(chunk: Chunk) -> str:
        async with semaphore:
            return await map_fn(chunk)
    
    # Map phase - parallel processing
    tasks = [limited_map(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    
    # Reduce phase - combine results
    final_result = await reduce_fn(list(results))
    
    return final_result


def hierarchical_chunk(
    text: str,
    levels: list[int] = [50000, 10000, 2000],
) -> dict:
    """
    Create hierarchical chunking for very large documents.
    
    Example: 1M doc -> 20 x 50K chunks -> 100 x 10K chunks -> 500 x 2K chunks
    
    This enables logarithmic-time traversal of large documents.
    
    Args:
        text: Full document
        levels: Chunk sizes at each level (large to small)
        
    Returns:
        Hierarchical structure of chunks
    """
    result = {
        "text_length": len(text),
        "levels": [],
    }
    
    current_texts = [text]
    
    for level_size in levels:
        level_chunks = []
        for t in current_texts:
            chunks = smart_chunk(t, target_size=level_size, overlap=100)
            level_chunks.extend(chunks)
        
        result["levels"].append({
            "chunk_size": level_size,
            "num_chunks": len(level_chunks),
            "chunks": level_chunks,
        })
        
        current_texts = [c.text for c in level_chunks]
    
    return result


class AdaptiveChunker:
    """
    Adapts chunk size based on content complexity.
    
    - Dense technical content -> smaller chunks
    - Simple prose -> larger chunks
    """
    
    def __init__(
        self,
        min_chunk_size: int = 1000,
        max_chunk_size: int = 8000,
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def estimate_complexity(self, text: str) -> float:
        """
        Estimate text complexity (0-1 scale).
        
        Factors:
        - Code blocks
        - Numbers/equations
        - Technical terms
        - Sentence length
        """
        score = 0.5  # baseline
        
        # Code blocks increase complexity
        code_blocks = len(re.findall(r'```', text))
        score += min(0.2, code_blocks * 0.02)
        
        # Numbers increase complexity
        numbers = len(re.findall(r'\d+\.?\d*', text))
        score += min(0.15, numbers / 100)
        
        # Long words (technical terms) increase complexity
        long_words = len(re.findall(r'\b\w{12,}\b', text))
        score += min(0.15, long_words / 50)
        
        return min(1.0, score)
    
    def chunk(self, text: str) -> list[Chunk]:
        """Chunk text with adaptive sizing."""
        complexity = self.estimate_complexity(text)
        
        # Higher complexity -> smaller chunks
        target_size = int(
            self.max_chunk_size - 
            (self.max_chunk_size - self.min_chunk_size) * complexity
        )
        
        return smart_chunk(text, target_size=target_size)
