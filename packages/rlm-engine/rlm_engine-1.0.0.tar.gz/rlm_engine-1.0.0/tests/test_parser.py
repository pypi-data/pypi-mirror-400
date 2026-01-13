"""Tests for parser module."""
import pytest
from rlm.parser import extract_code_blocks, extract_final_answer, format_code_output


class TestExtractCodeBlocks:
    """Tests for extract_code_blocks function."""
    
    def test_single_python_block(self):
        text = """Here's some code:
```python
print("hello")
```
That's it."""
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert 'print("hello")' in blocks[0]
    
    def test_multiple_blocks(self):
        text = """
```python
x = 1
```
And then:
```python
y = 2
```
"""
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert "x = 1" in blocks[0]
        assert "y = 2" in blocks[1]
    
    def test_no_code_blocks(self):
        text = "Just plain text with no code."
        blocks = extract_code_blocks(text)
        assert len(blocks) == 0
    
    def test_generic_code_block(self):
        text = """
```
import re
```
"""
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1


class TestExtractFinalAnswer:
    """Tests for extract_final_answer function."""
    
    def test_quoted_string(self):
        text = 'The answer is FINAL("QUANTUM-7749")'
        answer = extract_final_answer(text)
        assert answer == "QUANTUM-7749"
    
    def test_single_quotes(self):
        text = "FINAL('hello world')"
        answer = extract_final_answer(text)
        assert answer == "hello world"
    
    def test_number(self):
        text = "FINAL(1000)"
        answer = extract_final_answer(text)
        assert answer == "1000"
    
    def test_final_colon_format(self):
        text = "FINAL: The secret code is ABC123"
        answer = extract_final_answer(text)
        assert "ABC123" in answer
    
    def test_ignores_final_in_code_block(self):
        text = """
```python
if found:
    FINAL(matches[0])
```
After the code.
"""
        answer = extract_final_answer(text)
        # Should not extract variable names from code
        assert answer is None or "matches" not in answer
    
    def test_no_final(self):
        text = "Just some text without any final answer."
        answer = extract_final_answer(text)
        assert answer is None


class TestFormatCodeOutput:
    """Tests for format_code_output function."""
    
    def test_stdout_only(self):
        output = format_code_output("Hello world", "")
        assert output == "Hello world"
    
    def test_stderr_included(self):
        output = format_code_output("", "Error occurred")
        assert "STDERR" in output
        assert "Error occurred" in output
    
    def test_no_output(self):
        output = format_code_output("", "")
        assert output == "(no output)"
    
    def test_truncation(self):
        long_output = "x" * 5000
        output = format_code_output(long_output, "", max_length=1000)
        assert len(output) < 5000
        assert "truncated" in output.lower()
