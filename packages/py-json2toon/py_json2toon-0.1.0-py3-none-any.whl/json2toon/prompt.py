"""
Prompt helper functions for LLM interactions.
"""
from typing import Optional


def create_llm_prompt(
    data_toon: str,
    instruction: str,
    system_msg: Optional[str] = None
) -> str:
    """
    Create LLM prompt with TOON data.
    
    Args:
        data_toon: Data in TOON format
        instruction: Task instruction
        system_msg: Optional system message
        
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    if system_msg:
        prompt_parts.append(f"System: {system_msg}\n")
    
    prompt_parts.append(f"Data (TOON format):\n{data_toon}\n")
    prompt_parts.append(f"Task: {instruction}")
    
    return "\n".join(prompt_parts)


def create_response_template(expected_fields: list[str]) -> str:
    """
    Create TOON response template.
    
    Args:
        expected_fields: List of field names
        
    Returns:
        TOON template string
    """
    lines = []
    for field in expected_fields:
        lines.append(f"{field}:")
    
    return "\n".join(lines)


def wrap_in_code_fence(content: str, lang: str = "toon") -> str:
    """
    Wrap content in markdown code fence.
    
    Args:
        content: Content to wrap
        lang: Language identifier
        
    Returns:
        Content wrapped in code fence
    """
    return f"```{lang}\n{content}\n```"


def add_system_prompt(base_prompt: str, system_msg: str) -> str:
    """
    Add system message to prompt.
    
    Args:
        base_prompt: Base prompt
        system_msg: System message
        
    Returns:
        Combined prompt
    """
    return f"System: {system_msg}\n\n{base_prompt}"
