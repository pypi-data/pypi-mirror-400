"""Structured logging configuration for RLM."""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, asdict


class RLMLogger:
    """Structured logger for RLM operations."""
    
    def __init__(self, name: str = "rlm", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(RLMFormatter())
            self.logger.addHandler(handler)
        
        self.metrics = RLMMetrics()
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra={"data": kwargs})
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra={"data": kwargs})
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra={"data": kwargs})
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra={"data": kwargs})
    
    def iteration(self, iteration: int, depth: int, tokens_used: int = 0, 
                  code_executed: bool = False, output_length: int = 0):
        """Log an RLM iteration."""
        self.metrics.iterations += 1
        self.metrics.total_tokens += tokens_used
        
        self.info(
            "rlm_iteration",
            iteration=iteration,
            depth=depth,
            tokens_used=tokens_used,
            code_executed=code_executed,
            output_length=output_length,
        )
    
    def completion(self, query: str, context_size: int, answer: str,
                   iterations: int, llm_calls: int, duration: float, success: bool):
        """Log a completed RLM request."""
        self.metrics.requests += 1
        if success:
            self.metrics.successes += 1
        self.metrics.total_duration += duration
        self.metrics.total_llm_calls += llm_calls
        
        self.info(
            "rlm_completion",
            query_preview=query[:100],
            context_size=context_size,
            answer_preview=answer[:100] if answer else None,
            iterations=iterations,
            llm_calls=llm_calls,
            duration=duration,
            success=success,
        )
    
    def code_execution(self, code_preview: str, duration: float, 
                       success: bool, output_preview: str = ""):
        """Log code execution."""
        self.info(
            "code_execution",
            code_preview=code_preview[:200],
            duration=duration,
            success=success,
            output_preview=output_preview[:200],
        )
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        return asdict(self.metrics)


class RLMFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "data") and record.data:
            log_data.update(record.data)
        
        if os.getenv("RLM_LOG_FORMAT") == "json":
            return json.dumps(log_data)
        else:
            # Human-readable format
            extra = ""
            if hasattr(record, "data") and record.data:
                extra = " | " + " ".join(f"{k}={v}" for k, v in record.data.items())
            return f"{log_data['timestamp']} [{record.levelname}] {record.getMessage()}{extra}"


@dataclass
class RLMMetrics:
    """Metrics collected during RLM operations."""
    requests: int = 0
    successes: int = 0
    iterations: int = 0
    total_tokens: int = 0
    total_llm_calls: int = 0
    total_duration: float = 0.0
    
    @property
    def success_rate(self) -> float:
        return self.successes / self.requests if self.requests > 0 else 0.0
    
    @property
    def avg_duration(self) -> float:
        return self.total_duration / self.requests if self.requests > 0 else 0.0
    
    @property
    def avg_iterations(self) -> float:
        return self.iterations / self.requests if self.requests > 0 else 0.0


# Global logger instance
_logger: Optional[RLMLogger] = None


def get_logger() -> RLMLogger:
    """Get the global RLM logger."""
    global _logger
    if _logger is None:
        level = os.getenv("RLM_LOG_LEVEL", "INFO")
        _logger = RLMLogger(level=level)
    return _logger


def configure_logging(level: str = "INFO", json_format: bool = False):
    """Configure logging for RLM."""
    if json_format:
        os.environ["RLM_LOG_FORMAT"] = "json"
    
    global _logger
    _logger = RLMLogger(level=level)
    return _logger
