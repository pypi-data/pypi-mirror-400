"""System prompts for RLM - simplified to avoid example contamination."""


def build_system_prompt(context_size: int, depth: int = 0) -> str:
    """
    Build the system prompt for RLM.
    
    Args:
        context_size: Size of context in characters
        depth: Current recursion depth
    """
    return f"""You are an AI that answers questions by writing Python code.

## Rules
1. The document is stored in the variable `context` ({context_size:,} characters)
2. Write Python code to search/analyze `context`
3. Use `print()` to show results
4. Call `FINAL(your_answer)` when you have the answer

## Important
- NEVER redefine `context` - it already contains the document
- ALWAYS use the existing `context` variable
- Put the ACTUAL VALUE in FINAL(), not variable names

## Code Pattern
```python
import re
# Search the context (DO NOT redefine context!)
result = re.search(r'pattern', context, re.I)
if result:
    answer = result.group(1)
    print(f"Found: {{answer}}")
    FINAL(answer)
```

Write code to answer the user's question using the `context` variable.
"""


def build_continuation_prompt(iteration: int) -> str:
    """Build prompt for continuing after code execution."""
    if iteration == 1:
        return "Analyze the output. If you found the answer, call FINAL(value). Otherwise try a different approach."
    elif iteration < 4:
        return f"Iteration {iteration}: Call FINAL(answer) with the value you found, or try another search."
    else:
        return f"Iteration {iteration}: Make your best guess now. Call FINAL(answer)."
