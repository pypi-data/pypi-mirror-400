"""Tests for REPL module."""
import pytest
from rlm.repl import PythonREPL, REPLResult, FinalAnswerException


class TestPythonREPL:
    """Tests for PythonREPL class."""
    
    @pytest.fixture
    def repl(self):
        """Create a basic REPL instance."""
        def mock_llm_query(prompt):
            return f"Mock response to: {prompt[:50]}"
        
        return PythonREPL(
            context="Test document with some content.",
            llm_query_fn=mock_llm_query,
        )
    
    def test_simple_print(self, repl):
        result = repl.execute('print("hello")')
        assert result.success
        assert "hello" in result.stdout
    
    def test_context_access(self, repl):
        result = repl.execute('print(len(context))')
        assert result.success
        assert "32" in result.stdout  # Length of test context
    
    def test_regex_import(self, repl):
        result = repl.execute('''
import re
matches = re.findall(r'\\w+', context)
print(len(matches))
''')
        assert result.success
        assert result.stdout.strip().isdigit()
    
    def test_final_function(self, repl):
        result = repl.execute('FINAL("my answer")')
        assert result.success
        assert result.final_answer == "my answer"
    
    def test_final_with_number(self, repl):
        result = repl.execute('FINAL(42)')
        assert result.success
        assert result.final_answer == "42"
    
    def test_final_with_variable(self, repl):
        result = repl.execute('''
x = "computed value"
FINAL(x)
''')
        assert result.success
        assert result.final_answer == "computed value"
    
    def test_syntax_error(self, repl):
        result = repl.execute('if True print("bad")')
        assert not result.success
        assert "SyntaxError" in result.stderr
    
    def test_runtime_error(self, repl):
        result = repl.execute('x = 1/0')
        assert not result.success
        assert "ZeroDivisionError" in result.stderr
    
    def test_persistent_state(self, repl):
        repl.execute('my_var = 123')
        result = repl.execute('print(my_var)')
        assert result.success
        assert "123" in result.stdout
    
    def test_llm_query_available(self, repl):
        result = repl.execute('''
response = llm_query("test prompt")
print(type(response))
''')
        assert result.success
        assert "str" in result.stdout
    
    def test_json_module(self, repl):
        result = repl.execute('''
import json
data = json.dumps({"key": "value"})
print(data)
''')
        assert result.success
        assert "key" in result.stdout
    
    def test_math_operations(self, repl):
        result = repl.execute('''
import math
print(math.sqrt(16))
''')
        assert result.success
        assert "4" in result.stdout
    
    def test_reset(self, repl):
        repl.execute('x = 100')
        repl.reset()
        result = repl.execute('print(x)')
        assert not result.success  # x should not exist after reset


class TestREPLResult:
    """Tests for REPLResult dataclass."""
    
    def test_default_values(self):
        result = REPLResult()
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.success is True
        assert result.final_answer is None
    
    def test_with_values(self):
        result = REPLResult(
            stdout="output",
            stderr="",
            success=True,
            final_answer="answer"
        )
        assert result.final_answer == "answer"
