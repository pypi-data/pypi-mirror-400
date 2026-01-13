"""LLM Client Factory - Multi-backend support."""

from typing import Literal
from .base import BaseLLMClient, LLMResponse
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient

Backend = Literal["openai", "anthropic", "vllm", "ollama"]


def create_client(
    backend: Backend = "openai",
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    **kwargs,
) -> BaseLLMClient:
    """
    Factory function to create LLM client.
    
    Args:
        backend: One of "openai", "anthropic", "vllm", "ollama"
        model: Model name
        base_url: API endpoint (required for vLLM/Ollama)
        api_key: API key (uses env var if not provided)
    
    Examples:
        # OpenAI API (cloud - no deployment needed)
        client = create_client(backend="openai", model="gpt-4o-mini")
        
        # Anthropic API (cloud - no deployment needed)
        client = create_client(backend="anthropic", model="claude-sonnet-4-20250514")
        
        # vLLM (self-hosted - requires deployed model)
        client = create_client(
            backend="vllm",
            model="meta-llama/Llama-3.1-8B-Instruct",
            base_url="http://localhost:8000/v1"
        )
        
        # Ollama (local - requires ollama running)
        client = create_client(backend="ollama", model="llama3.2")
    """
    
    if backend == "openai":
        return OpenAIClient(
            model=model or "gpt-4o-mini",
            api_key=api_key,
            **kwargs,
        )
    
    elif backend == "anthropic":
        return AnthropicClient(
            model=model or "claude-sonnet-4-20250514",
            api_key=api_key,
            **kwargs,
        )
    
    elif backend == "vllm":
        if not base_url:
            base_url = "http://localhost:8000/v1"
        return OpenAIClient(
            model=model or "meta-llama/Llama-3.1-8B-Instruct",
            base_url=base_url,
            api_key=api_key or "EMPTY",
            **kwargs,
        )
    
    elif backend == "ollama":
        return OpenAIClient(
            model=model or "llama3.2",
            base_url=base_url or "http://localhost:11434/v1",
            api_key=api_key or "ollama",
            **kwargs,
        )
    
    else:
        raise ValueError(f"Unknown backend: {backend}. Use: openai, anthropic, vllm, ollama")


__all__ = ["create_client", "BaseLLMClient", "LLMResponse", "Backend"]
