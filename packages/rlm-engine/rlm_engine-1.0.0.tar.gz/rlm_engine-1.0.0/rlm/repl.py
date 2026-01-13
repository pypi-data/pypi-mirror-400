"""Safe Python REPL for executing LLM-generated code."""

import sys
import io
import re
import json
import traceback
from typing import Any, Callable
from dataclasses import dataclass, field


class FinalAnswerException(Exception):
    """Raised when FINAL() is called with an answer."""
    def __init__(self, answer: str):
        self.answer = answer
        super().__init__(f"FINAL: {answer}")


@dataclass
class REPLResult:
    """Result from code execution."""
    stdout: str = ""
    stderr: str = ""
    success: bool = True
    locals_snapshot: dict = field(default_factory=dict)
    execution_time: float = 0.0
    final_answer: str | None = None  # Captured from FINAL() call


class PythonREPL:
    """
    Execute Python code in a controlled environment.
    
    Provides:
    - Persistent state across executions
    - Access to context variable
    - Recursive LLM query functions
    - Basic safety restrictions
    """
    
    # Safe built-in modules
    SAFE_MODULES = {
        "re", "json", "math", "datetime", "collections",
        "itertools", "functools", "operator", "string",
    }
    
    def __init__(
        self,
        context: str,
        llm_query_fn: Callable[[str], str],
        llm_query_batch_fn: Callable[[list[str]], list[str]] | None = None,
        max_output_chars: int = 5000,
    ):
        """
        Initialize REPL environment.
        
        Args:
            context: The document to analyze
            llm_query_fn: Function to call LLM recursively
            llm_query_batch_fn: Function to call LLM on multiple prompts in parallel
            max_output_chars: Maximum output length before truncation
        """
        self.context = context
        self.llm_query_fn = llm_query_fn
        self.llm_query_batch_fn = llm_query_batch_fn or self._default_batch
        self.max_output_chars = max_output_chars
        
        # FINAL function that captures answers
        def final_answer(answer):
            """Call this with your final answer to complete the task."""
            raise FinalAnswerException(str(answer))
        
        # Persistent local variables across executions
        self.local_vars: dict[str, Any] = {
            "context": context,
            "llm_query": llm_query_fn,
            "llm_query_batch": self.llm_query_batch_fn,
            "FINAL": final_answer,  # Add FINAL as a callable
        }
        
        # Build safe globals
        self.global_vars = self._build_safe_globals()
    
    def _default_batch(self, prompts: list[str]) -> list[str]:
        """Default batch implementation (sequential fallback)."""
        return [self.llm_query_fn(p) for p in prompts]
    
    def _build_safe_globals(self) -> dict[str, Any]:
        """Build a restricted globals dictionary."""
        safe_globals = {
            "__builtins__": {
                # Import support
                "__import__": __import__,
                
                # Types
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "frozenset": frozenset,
                "bytes": bytes,
                "type": type,
                
                # Iteration
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "reversed": reversed,
                "sorted": sorted,
                "iter": iter,
                "next": next,
                
                # Aggregation
                "sum": sum,
                "min": min,
                "max": max,
                "any": any,
                "all": all,
                "abs": abs,
                "round": round,
                
                # String
                "chr": chr,
                "ord": ord,
                "repr": repr,
                "format": format,
                "print": print,
                
                # Containers
                "hasattr": hasattr,
                "getattr": getattr,
                "setattr": setattr,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "callable": callable,
                
                # Constants
                "True": True,
                "False": False,
                "None": None,
                
                # Exceptions
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError,
            },
            "__name__": "__main__",
        }
        
        # Add safe modules
        import re as re_module
        import json as json_module
        import math as math_module
        from datetime import datetime, timedelta
        from collections import Counter, defaultdict
        
        safe_globals.update({
            "re": re_module,
            "json": json_module,
            "math": math_module,
            "datetime": datetime,
            "timedelta": timedelta,
            "Counter": Counter,
            "defaultdict": defaultdict,
        })
        
        return safe_globals
    
    def execute(self, code: str) -> REPLResult:
        """
        Execute Python code and return results.
        
        Args:
            code: Python code to execute
            
        Returns:
            REPLResult with stdout, stderr, and success status
        """
        import time
        start_time = time.perf_counter()
        
        # Capture stdout/stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        
        try:
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            # Merge globals and locals for execution
            exec_globals = {**self.global_vars}
            exec_locals = {**self.local_vars}
            
            # Execute the code
            exec(code, exec_globals, exec_locals)
            
            # Update persistent locals (excluding builtins)
            for key, value in exec_locals.items():
                if key not in self.global_vars and not key.startswith("_"):
                    self.local_vars[key] = value
            
            stdout = stdout_buffer.getvalue()
            stderr = stderr_buffer.getvalue()
            
            # Truncate if too long
            if len(stdout) > self.max_output_chars:
                stdout = stdout[:self.max_output_chars] + \
                         f"\n\n[Truncated: {len(stdout)} chars total]"
            
            execution_time = time.perf_counter() - start_time
            
            return REPLResult(
                stdout=stdout,
                stderr=stderr,
                success=True,
                locals_snapshot=self._snapshot_locals(),
                execution_time=execution_time,
            )
            
        except FinalAnswerException as e:
            # FINAL() was called - this is success!
            stdout = stdout_buffer.getvalue()
            return REPLResult(
                stdout=stdout + f"\n>>> FINAL ANSWER: {e.answer}",
                stderr="",
                success=True,
                locals_snapshot=self._snapshot_locals(),
                execution_time=time.perf_counter() - start_time,
                final_answer=e.answer,
            )
            
        except Exception as e:
            stderr = stderr_buffer.getvalue()
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            return REPLResult(
                stdout=stdout_buffer.getvalue(),
                stderr=stderr + error_msg,
                success=False,
                locals_snapshot=self._snapshot_locals(),
                execution_time=time.perf_counter() - start_time,
            )
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _snapshot_locals(self) -> dict:
        """Create a serializable snapshot of local variables."""
        snapshot = {}
        for key, value in self.local_vars.items():
            if key in ("context", "llm_query", "llm_query_batch"):
                continue  # Skip large/callable items
            try:
                # Try to get a short repr
                r = repr(value)
                if len(r) > 100:
                    r = r[:100] + "..."
                snapshot[key] = r
            except Exception:
                snapshot[key] = f"<{type(value).__name__}>"
        return snapshot
    
    def reset(self):
        """Reset the REPL state."""
        self.local_vars = {
            "context": self.context,
            "llm_query": self.llm_query_fn,
            "llm_query_batch": self.llm_query_batch_fn,
        }
