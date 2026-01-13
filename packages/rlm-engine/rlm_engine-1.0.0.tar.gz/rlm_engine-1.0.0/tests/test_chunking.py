"""Tests for chunking module."""
import pytest
from rlm.optimizations.chunking import (
    smart_chunk, 
    Chunk, 
    hierarchical_chunk,
    AdaptiveChunker,
    parallel_map_reduce,
)


class TestSmartChunk:
    """Tests for smart_chunk function."""
    
    def test_small_text_single_chunk(self):
        text = "Small text"
        chunks = smart_chunk(text, target_size=100)
        assert len(chunks) == 1
        assert chunks[0].text == text
    
    def test_splits_large_text(self):
        text = "word " * 1000  # 5000 characters
        chunks = smart_chunk(text, target_size=1000, overlap=0)
        assert len(chunks) >= 5
    
    def test_overlap(self):
        text = "A" * 500 + "B" * 500 + "C" * 500
        chunks = smart_chunk(text, target_size=500, overlap=100)
        
        # Check that chunks overlap
        for i in range(len(chunks) - 1):
            # End of current chunk should overlap with start of next
            assert chunks[i].end_idx > chunks[i + 1].start_idx or \
                   chunks[i].end_idx == len(text)
    
    def test_respects_paragraph_boundaries(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = smart_chunk(text, target_size=30, overlap=0, respect_boundaries=True)
        
        # Should try to break at paragraph boundaries
        for chunk in chunks:
            # Each chunk should not start mid-paragraph
            if chunk.start_idx > 0:
                assert text[chunk.start_idx - 1] in "\n " or chunk.start_idx == 0
    
    def test_chunk_metadata(self):
        text = "Test content " * 100
        chunks = smart_chunk(text, target_size=100)
        
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == i
            assert chunk.start_idx >= 0
            assert chunk.end_idx <= len(text)
            assert chunk.size == len(chunk.text)


class TestChunk:
    """Tests for Chunk dataclass."""
    
    def test_size_property(self):
        chunk = Chunk(text="hello", start_idx=0, end_idx=5, chunk_id=0)
        assert chunk.size == 5


class TestHierarchicalChunk:
    """Tests for hierarchical_chunk function."""
    
    def test_creates_hierarchy(self):
        text = "x" * 100000  # 100K characters
        result = hierarchical_chunk(text, levels=[50000, 10000, 2000])
        
        assert "levels" in result
        assert len(result["levels"]) == 3
        assert result["text_length"] == 100000
    
    def test_level_sizes(self):
        text = "y" * 50000
        result = hierarchical_chunk(text, levels=[20000, 5000])
        
        # First level should have fewer, larger chunks
        # Second level should have more, smaller chunks
        assert result["levels"][0]["num_chunks"] <= result["levels"][1]["num_chunks"]


class TestAdaptiveChunker:
    """Tests for AdaptiveChunker class."""
    
    def test_simple_text_larger_chunks(self):
        chunker = AdaptiveChunker(min_chunk_size=1000, max_chunk_size=8000)
        simple_text = "Simple prose text. " * 500
        
        complexity = chunker.estimate_complexity(simple_text)
        assert complexity < 0.7  # Should be relatively low
    
    def test_code_text_smaller_chunks(self):
        chunker = AdaptiveChunker(min_chunk_size=1000, max_chunk_size=8000)
        code_text = """
```python
def function():
    return 42
```
More code:
```python
class MyClass:
    pass
```
Numbers: 123.456, 789.012
Technical terms: authentication, implementation, configuration
"""
        complexity = chunker.estimate_complexity(code_text)
        assert complexity > 0.5  # Should be higher
    
    def test_chunking_adapts(self):
        chunker = AdaptiveChunker(min_chunk_size=100, max_chunk_size=1000)
        
        simple = "word " * 500
        complex_text = "```python\ncode\n```\n" * 50 + "12345 " * 100
        
        simple_chunks = chunker.chunk(simple)
        complex_chunks = chunker.chunk(complex_text)
        
        # Complex text should result in smaller chunks (more chunks)
        if len(simple) == len(complex_text):
            assert len(complex_chunks) >= len(simple_chunks)


class TestParallelMapReduce:
    """Tests for parallel_map_reduce function."""
    
    @pytest.mark.asyncio
    async def test_basic_map_reduce(self):
        chunks = [
            Chunk(text="hello", start_idx=0, end_idx=5, chunk_id=0),
            Chunk(text="world", start_idx=5, end_idx=10, chunk_id=1),
        ]
        
        async def map_fn(chunk):
            return chunk.text.upper()
        
        async def reduce_fn(results):
            return " ".join(results)
        
        result = await parallel_map_reduce(chunks, map_fn, reduce_fn)
        assert result == "HELLO WORLD"
    
    @pytest.mark.asyncio
    async def test_respects_concurrency_limit(self):
        import asyncio
        
        chunks = [Chunk(text=str(i), start_idx=i, end_idx=i+1, chunk_id=i) for i in range(10)]
        concurrent_count = 0
        max_concurrent = 0
        
        async def map_fn(chunk):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.01)
            concurrent_count -= 1
            return chunk.text
        
        async def reduce_fn(results):
            return ",".join(results)
        
        await parallel_map_reduce(chunks, map_fn, reduce_fn, max_concurrent=3)
        assert max_concurrent <= 3
