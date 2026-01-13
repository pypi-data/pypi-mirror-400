"""Base LLM Client Interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    usage: dict = field(default_factory=dict)
    model: str = ""
    finish_reason: str = ""


@dataclass 
class LLMUsage:
    """Token usage statistics."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    def __add__(self, other: "LLMUsage") -> "LLMUsage":
        return LLMUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self):
        self._total_usage = LLMUsage()
        self._call_count = 0
    
    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Synchronous chat completion."""
        pass
    
    @abstractmethod
    async def achat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Asynchronous chat completion."""
        pass
    
    async def achat_completion_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming chat completion (optional override)."""
        response = await self.achat_completion(messages, temperature, max_tokens)
        yield response.content
    
    @abstractmethod
    def close(self):
        """Clean up resources."""
        pass
    
    @property
    def usage(self) -> LLMUsage:
        """Get total usage across all calls."""
        return self._total_usage
    
    @property
    def call_count(self) -> int:
        """Get total number of API calls."""
        return self._call_count
    
    def _track_usage(self, usage: dict):
        """Track usage from API response."""
        self._call_count += 1
        self._total_usage += LLMUsage(
            input_tokens=usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            output_tokens=usage.get("completion_tokens", usage.get("output_tokens", 0)),
            total_tokens=usage.get("total_tokens", 0),
        )
