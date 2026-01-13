"""Integration tests for RLM with mock LLM."""
import pytest
from unittest.mock import Mock, patch
from rlm import RLM, RLMConfig


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_index = 0
        self.call_count = 0
        
    def chat_completion(self, messages, **kwargs):
        self.call_count += 1
        response_text = self.responses[min(self.call_index, len(self.responses) - 1)]
        self.call_index += 1
        
        mock_response = Mock()
        mock_response.content = response_text
        mock_response.model = "mock-model"
        return mock_response
    
    async def achat_completion(self, messages, **kwargs):
        return self.chat_completion(messages, **kwargs)
    
    @property
    def usage(self):
        mock_usage = Mock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 50
        return mock_usage
    
    def close(self):
        pass


class TestRLMIntegration:
    """Integration tests for RLM."""
    
    def test_simple_extraction(self):
        """Test that RLM can extract a value using code."""
        responses = [
            '''I'll search for the code.
```python
import re
matches = re.findall(r'code[:\\s]+(\\w+)', context, re.I)
print(f"Found: {matches}")
FINAL(matches[0] if matches else "Not found")
```
''',
        ]
        
        mock_client = MockLLMClient(responses)
        config = RLMConfig(max_iterations=3, verbose=False)
        
        rlm = RLM(backend="openai", config=config)
        rlm.client = mock_client
        
        result = rlm.completion(
            query="Find the code",
            context="Secret code: ABC123"
        )
        
        assert result.success
        assert "ABC123" in result.answer
    
    def test_direct_final_answer(self):
        """Test when LLM provides FINAL directly."""
        responses = [
            'FINAL("42")',
        ]
        
        mock_client = MockLLMClient(responses)
        config = RLMConfig(max_iterations=3, verbose=False)
        
        rlm = RLM(backend="openai", config=config)
        rlm.client = mock_client
        
        result = rlm.completion(
            query="What is the answer?",
            context="The answer is 42."
        )
        
        assert result.success
        assert "42" in result.answer
    
    def test_multi_iteration(self):
        """Test that RLM can use multiple iterations."""
        responses = [
            '''Let me explore first.
```python
print(len(context))
```
''',
            '''Now I'll search.
```python
import re
match = re.search(r'password[:\\s]+(\\S+)', context, re.I)
if match:
    FINAL(match.group(1))
```
''',
        ]
        
        mock_client = MockLLMClient(responses)
        config = RLMConfig(max_iterations=5, verbose=False)
        
        rlm = RLM(backend="openai", config=config)
        rlm.client = mock_client
        
        result = rlm.completion(
            query="Find password",
            context="User password: secret123"
        )
        
        assert result.iterations >= 1
        assert mock_client.call_count >= 1
    
    def test_max_iterations_reached(self):
        """Test behavior when max iterations is reached."""
        responses = [
            '''```python
print("exploring...")
```
''',
        ] * 10
        
        mock_client = MockLLMClient(responses)
        config = RLMConfig(max_iterations=3, verbose=False)
        
        rlm = RLM(backend="openai", config=config)
        rlm.client = mock_client
        
        result = rlm.completion(
            query="Find something",
            context="Some context"
        )
        
        assert result.iterations == 3
        assert not result.success or "max iterations" in result.answer.lower()


class TestRLMConfig:
    """Tests for RLMConfig."""
    
    def test_default_config(self):
        config = RLMConfig()
        assert config.max_iterations == 20
        assert config.max_depth == 3
        assert config.temperature == 0.7
    
    def test_custom_config(self):
        config = RLMConfig(
            max_iterations=5,
            max_depth=2,
            temperature=0.5,
            verbose=False
        )
        assert config.max_iterations == 5
        assert config.max_depth == 2
        assert config.temperature == 0.5
        assert config.verbose is False
