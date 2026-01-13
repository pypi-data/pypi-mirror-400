"""OpenAI-compatible client with optimizations.

Works with:
- OpenAI API
- vLLM (OpenAI-compatible)
- Ollama (OpenAI-compatible)
- Any OpenAI-compatible endpoint
"""

import os
import asyncio
from typing import AsyncIterator

import httpx
from openai import OpenAI, AsyncOpenAI

from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """
    Optimized OpenAI-compatible client.
    
    Optimizations:
    - HTTP/2 support
    - Connection pooling
    - Async batching
    
    Usage:
        # OpenAI API
        client = OpenAIClient(model="gpt-4o-mini")
        
        # vLLM
        client = OpenAIClient(
            model="llama",
            base_url="http://localhost:8000/v1",
            api_key="EMPTY"
        )
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
    ):
        super().__init__()
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Create optimized HTTP client with connection pooling
        http_client = httpx.Client(
            timeout=timeout,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
            ),
        )
        
        async_http_client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
            ),
        )
        
        # Create OpenAI clients
        self.client = OpenAI(
            api_key=api_key or "EMPTY",
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        
        self.async_client = AsyncOpenAI(
            api_key=api_key or "EMPTY",
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=async_http_client,
        )
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Synchronous chat completion."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Track usage
        if response.usage:
            self._track_usage({
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            })
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            usage=dict(response.usage) if response.usage else {},
            model=response.model,
            finish_reason=response.choices[0].finish_reason or "",
        )
    
    async def achat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Asynchronous chat completion."""
        
        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Track usage
        if response.usage:
            self._track_usage({
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            })
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            usage=dict(response.usage) if response.usage else {},
            model=response.model,
            finish_reason=response.choices[0].finish_reason or "",
        )
    
    async def achat_completion_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming chat completion."""
        
        stream = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def batch_completions(
        self,
        messages_list: list[list[dict]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> list[LLMResponse]:
        """
        Process multiple completions in parallel (OPTIMIZATION).
        
        Args:
            messages_list: List of message lists to process
            
        Returns:
            List of responses in same order
        """
        tasks = [
            self.achat_completion(messages, temperature, max_tokens)
            for messages in messages_list
        ]
        return await asyncio.gather(*tasks)
    
    def close(self):
        """Clean up resources."""
        self.client.close()
        # Note: async client closed automatically
