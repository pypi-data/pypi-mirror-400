"""
RLM - Recursive Language Model

Process unlimited context by having LLMs write code to analyze documents.

Example:
    from rlm import RLM, RLMConfig
    
    rlm = RLM(backend="openai", model="gpt-4o")
    result = rlm.completion(
        query="What is the revenue?",
        context=huge_document,
    )
    print(result.answer)
"""

from .core import RLM, RLMResult, RLMConfig
from .fast_rlm import FastRLM, FastRLMResult
from .scalable_rlm import ScalableRLM, ScalableRLMResult
from .config import RLMSettings, load_config
from .streaming import StreamingRLM, StreamEvent

__version__ = "1.0.0"

__all__ = [
    # Core
    "RLM",
    "RLMResult", 
    "RLMConfig",
    # Optimized variants
    "FastRLM",
    "FastRLMResult",
    "ScalableRLM",
    "ScalableRLMResult",
    # Config
    "RLMSettings",
    "load_config",
    # Streaming
    "StreamingRLM",
    "StreamEvent",
]
