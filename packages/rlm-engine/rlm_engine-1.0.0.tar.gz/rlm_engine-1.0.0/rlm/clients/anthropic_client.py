"""Anthropic Claude client."""

import os
from typing import AsyncIterator

from anthropic import Anthropic, AsyncAnthropic

from .base import BaseLLMClient, LLMResponse


class AnthropicClient(BaseLLMClient):
    """
    Client for Anthropic Claude API.
    
    Usage:
        client = AnthropicClient(model="claude-sonnet-4-20250514")
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
    ):
        super().__init__()
        self.model = model
        
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        self.client = Anthropic(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        
        self.async_client = AsyncAnthropic(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
    
    def _extract_system_and_messages(
        self, messages: list[dict]
    ) -> tuple[str, list[dict]]:
        """Separate system message from conversation."""
        system_msg = ""
        conversation = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)
        
        return system_msg, conversation
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Synchronous chat completion."""
        
        system_msg, conversation = self._extract_system_and_messages(messages)
        
        response = self.client.messages.create(
            model=self.model,
            system=system_msg,
            messages=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Track usage
        self._track_usage({
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        })
        
        return LLMResponse(
            content=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            model=response.model,
            finish_reason=response.stop_reason or "",
        )
    
    async def achat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Asynchronous chat completion."""
        
        system_msg, conversation = self._extract_system_and_messages(messages)
        
        response = await self.async_client.messages.create(
            model=self.model,
            system=system_msg,
            messages=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Track usage
        self._track_usage({
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        })
        
        return LLMResponse(
            content=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            model=response.model,
            finish_reason=response.stop_reason or "",
        )
    
    async def achat_completion_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming chat completion."""
        
        system_msg, conversation = self._extract_system_and_messages(messages)
        
        async with self.async_client.messages.stream(
            model=self.model,
            system=system_msg,
            messages=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def close(self):
        """Clean up resources."""
        pass  # Anthropic clients don't need explicit cleanup
