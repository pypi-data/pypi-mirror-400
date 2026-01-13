"""
Token counting and comparison metrics.
"""
import json
from typing import Any, Dict
from dataclasses import dataclass
import tiktoken
from .exceptions import AnalysisError


@dataclass
class ComparisonResult:
    """Results of comparing JSON vs TOON formats."""
    json_tokens: int
    toon_tokens: int
    savings: int
    savings_percent: float


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Text to count
        encoding_name: Tiktoken encoding to use
        
    Returns:
        Token count
        
    Raises:
        AnalysisError: If token counting fails
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        raise AnalysisError(f"Failed to count tokens: {e}") from e


def compare_formats(
    data: Any,
    encoder,
    encoding_name: str = "cl100k_base"
) -> ComparisonResult:
    """
    Compare token counts between JSON and TOON.
    
    Args:
        data: Data to compare
        encoder: ToonEncoder instance
        encoding_name: Tiktoken encoding to use
        
    Returns:
        ComparisonResult with token counts
        
    Raises:
        AnalysisError: If comparison fails
    """
    try:
        # Get JSON representation
        json_str = json.dumps(data, indent=2)
        json_tokens = count_tokens(json_str, encoding_name)
        
        # Get TOON representation
        toon_str = encoder.encode(data)
        toon_tokens = count_tokens(toon_str, encoding_name)
        
        # Calculate savings
        savings = json_tokens - toon_tokens
        savings_percent = (
            (savings / json_tokens * 100) if json_tokens > 0 else 0
        )
        
        return ComparisonResult(
            json_tokens=json_tokens,
            toon_tokens=toon_tokens,
            savings=savings,
            savings_percent=savings_percent
        )
    except Exception as e:
        raise AnalysisError(f"Failed to compare formats: {e}") from e


def generate_report(
    comparison: ComparisonResult,
    output_format: str = "text"
) -> str:
    """
    Generate a comparison report.
    
    Args:
        comparison: ComparisonResult to report
        output_format: Output format (text, json, markdown)
        
    Returns:
        Formatted report string
        
    Raises:
        AnalysisError: If report generation fails
    """
    try:
        if output_format == "json":
            return json.dumps({
                "json_tokens": comparison.json_tokens,
                "toon_tokens": comparison.toon_tokens,
                "savings": comparison.savings,
                "savings_percent": round(comparison.savings_percent, 2)
            }, indent=2)
        
        elif output_format == "markdown":
            return f"""# Token Comparison Report

| Format | Tokens |
|--------|--------|
| JSON   | {comparison.json_tokens} |
| TOON   | {comparison.toon_tokens} |

**Savings:** {comparison.savings} tokens \
({comparison.savings_percent:.1f}%)
"""
        
        else:  # text
            return f"""Token Comparison Report:
- JSON tokens: {comparison.json_tokens}
- TOON tokens: {comparison.toon_tokens}
- Savings: {comparison.savings} tokens \
({comparison.savings_percent:.1f}%)"""
    
    except Exception as e:
        raise AnalysisError(f"Failed to generate report: {e}") from e
