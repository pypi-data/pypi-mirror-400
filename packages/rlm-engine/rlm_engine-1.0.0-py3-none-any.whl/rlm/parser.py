"""Parse LLM responses for code blocks and FINAL answers."""

import re
from typing import Optional


def extract_code_blocks(text: str) -> list[str]:
    """
    Extract Python code blocks from markdown-formatted text.
    
    Args:
        text: LLM response text
        
    Returns:
        List of code strings (without markdown fences)
    """
    # Match ```python ... ``` or ``` ... ```
    pattern = r'```(?:python)?\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Clean and filter
    code_blocks = []
    for match in matches:
        code = match.strip()
        if code:
            code_blocks.append(code)
    
    return code_blocks


def extract_final_answer(text: str) -> Optional[str]:
    """
    Extract FINAL("answer") from text, but NOT from inside code blocks.
    
    Supports multiple formats:
        FINAL("answer")
        FINAL('answer')
        FINAL: answer
        **FINAL**: answer
    
    Args:
        text: LLM response text
        
    Returns:
        The answer string if found, None otherwise
    """
    # First, remove code blocks to avoid extracting FINAL from code
    text_without_code = re.sub(r'```(?:python)?\s*\n.*?```', '', text, flags=re.DOTALL)
    
    # Try FINAL with quoted string (most reliable)
    pattern_quoted = r'FINAL\s*\(\s*["\']([^"\']+)["\']\s*\)'
    match = re.search(pattern_quoted, text_without_code)
    if match:
        return match.group(1).strip()
    
    # Try FINAL with unquoted value (for numbers, etc.)
    pattern_unquoted = r'FINAL\s*\(\s*([^()]+?)\s*\)'
    match = re.search(pattern_unquoted, text_without_code)
    if match:
        answer = match.group(1).strip()
        # Accept if it looks like a value (number, quoted string, etc.)
        if re.match(r'^[\d\-\.\$\,]+$', answer) or answer.startswith(('"', "'")):
            if answer.startswith(('"', "'")) and answer.endswith(('"', "'")):
                answer = answer[1:-1]
            return answer
    
    # Try FINAL: answer (outside code)
    pattern_colon = r'(?:\*\*)?FINAL(?:\*\*)?\s*:\s*["\']?([^"\'\n]+)["\']?'
    match = re.search(pattern_colon, text_without_code, re.IGNORECASE)
    if match:
        answer = match.group(1).strip()
        # Skip if it looks like a variable name
        if not re.match(r'^[a-z_][a-z0-9_]*$', answer):
            return answer
    
    # Try "The answer is:" pattern
    pattern_answer = r'(?:the\s+)?(?:final\s+)?answer\s*(?:is)?\s*:\s*["\']?([^"\'\n]+)["\']?'
    match = re.search(pattern_answer, text_without_code, re.IGNORECASE)
    if match:
        answer = match.group(1).strip()
        if len(answer) > 3:  # Avoid matching single words
            return answer
    
    # Check if the entire response is just a short answer (number, short phrase)
    clean_text = text_without_code.strip()
    if len(clean_text) < 50 and re.match(r'^[\d\$\,\.\-]+$', clean_text):
        return clean_text
    
    return None


def has_final_answer(text: str) -> bool:
    """Check if text contains a FINAL() statement."""
    return "FINAL(" in text or "FINAL (" in text


def format_code_output(stdout: str, stderr: str, max_length: int = 3000) -> str:
    """
    Format code execution output for LLM consumption.
    
    Args:
        stdout: Standard output from execution
        stderr: Standard error from execution
        max_length: Maximum output length
        
    Returns:
        Formatted output string
    """
    output = ""
    
    if stdout:
        output += stdout
    
    if stderr:
        output += f"\n⚠️ STDERR:\n{stderr}"
    
    if not output:
        output = "(no output)"
    
    # Truncate if too long
    if len(output) > max_length:
        output = output[:max_length] + f"\n\n[Output truncated: {len(output)} chars total]"
    
    return output
