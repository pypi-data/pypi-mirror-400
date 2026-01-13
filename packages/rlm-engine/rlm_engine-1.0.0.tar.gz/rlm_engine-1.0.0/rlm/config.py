"""Configuration management for RLM."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Literal

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class RLMSettings:
    """RLM configuration settings."""
    
    # Model settings
    backend: Literal["openai", "anthropic", "vllm", "ollama"] = "openai"
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    
    # RLM settings
    max_iterations: int = 10
    max_depth: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096
    verbose: bool = False
    
    # Optimization settings
    cache_enabled: bool = True
    cache_ttl: int = 3600
    parallel_chunks: int = 5
    use_relevance_filtering: bool = True
    
    # Server settings
    server_host: str = "0.0.0.0"
    server_port: int = 8080
    
    def __post_init__(self):
        """Apply environment variable overrides."""
        # Backend
        self.backend = os.getenv("RLM_BACKEND", self.backend)
        self.model = os.getenv("RLM_MODEL", self.model)
        self.base_url = os.getenv("RLM_BASE_URL", self.base_url) or os.getenv("VLLM_URL")
        self.api_key = os.getenv("RLM_API_KEY", self.api_key) or os.getenv("OPENAI_API_KEY")
        
        # RLM settings
        if os.getenv("RLM_MAX_ITERATIONS"):
            self.max_iterations = int(os.getenv("RLM_MAX_ITERATIONS"))
        if os.getenv("RLM_MAX_DEPTH"):
            self.max_depth = int(os.getenv("RLM_MAX_DEPTH"))
        if os.getenv("RLM_TEMPERATURE"):
            self.temperature = float(os.getenv("RLM_TEMPERATURE"))
        if os.getenv("RLM_VERBOSE"):
            self.verbose = os.getenv("RLM_VERBOSE").lower() in ("true", "1", "yes")


def load_config(config_path: Optional[str] = None) -> RLMSettings:
    """
    Load configuration from file and environment.
    
    Priority (highest to lowest):
    1. Environment variables
    2. Config file
    3. Defaults
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        RLMSettings instance
    """
    settings_dict = {}
    
    # Try to load from config file
    if config_path is None:
        # Check default locations
        for path in ["rlm.yaml", "rlm.yml", "config/rlm.yaml", ".rlm.yaml"]:
            if Path(path).exists():
                config_path = path
                break
    
    if config_path and Path(config_path).exists() and YAML_AVAILABLE:
        with open(config_path) as f:
            file_config = yaml.safe_load(f)
            if file_config:
                # Flatten nested config
                if "model" in file_config:
                    settings_dict.update(file_config["model"])
                if "rlm" in file_config:
                    settings_dict.update(file_config["rlm"])
                if "optimizations" in file_config:
                    settings_dict.update(file_config["optimizations"])
                if "server" in file_config:
                    settings_dict.update({
                        "server_host": file_config["server"].get("host", "0.0.0.0"),
                        "server_port": file_config["server"].get("port", 8080),
                    })
    
    # Create settings (env vars applied in __post_init__)
    return RLMSettings(**settings_dict)


def save_config(settings: RLMSettings, config_path: str = "rlm.yaml"):
    """Save configuration to YAML file."""
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML required for saving config: pip install pyyaml")
    
    config = {
        "model": {
            "backend": settings.backend,
            "model": settings.model,
            "base_url": settings.base_url,
        },
        "rlm": {
            "max_iterations": settings.max_iterations,
            "max_depth": settings.max_depth,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "verbose": settings.verbose,
        },
        "optimizations": {
            "cache_enabled": settings.cache_enabled,
            "cache_ttl": settings.cache_ttl,
            "parallel_chunks": settings.parallel_chunks,
            "use_relevance_filtering": settings.use_relevance_filtering,
        },
        "server": {
            "host": settings.server_host,
            "port": settings.server_port,
        },
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


# Example config file template
CONFIG_TEMPLATE = """
# RLM Configuration File
# Save as: rlm.yaml

model:
  backend: vllm  # openai, anthropic, vllm, ollama
  model: meta-llama/Llama-3.1-70B-Instruct
  base_url: http://localhost:8000/v1
  # api_key: your-api-key  # Or set RLM_API_KEY env var

rlm:
  max_iterations: 10
  max_depth: 3
  temperature: 0.7
  max_tokens: 4096
  verbose: false

optimizations:
  cache_enabled: true
  cache_ttl: 3600
  parallel_chunks: 5
  use_relevance_filtering: true

server:
  host: 0.0.0.0
  port: 8080
"""
