"""
Core convenience functions for json2toon library.
"""
import json
from typing import Any, Dict, Union, Optional
from pathlib import Path
from .config import ToonConfig, get_default_config
from .encoder import ToonEncoder
from .decoder import ToonDecoder
from .metrics import compare_formats, generate_report, ComparisonResult


def json_to_toon(
    data: Any,
    config: Optional[ToonConfig] = None
) -> str:
    """
    Convert JSON data to TOON format.
    
    Args:
        data: Python data to convert
        config: Optional ToonConfig
        
    Returns:
        TOON-formatted string
    """
    encoder = ToonEncoder(config or get_default_config())
    return encoder.encode(data)


def toon_to_json(
    toon_str: str,
    config: Optional[ToonConfig] = None
) -> Any:
    """
    Convert TOON format to JSON data.
    
    Args:
        toon_str: TOON-formatted string
        config: Optional ToonConfig
        
    Returns:
        Decoded Python data
    """
    decoder = ToonDecoder(config or get_default_config())
    return decoder.decode(toon_str)


def convert_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    to_toon: bool = True,
    config: Optional[ToonConfig] = None
) -> None:
    """
    Convert file between JSON and TOON formats.
    
    Args:
        input_path: Input file path
        output_path: Output file path
        to_toon: True for JSON→TOON, False for TOON→JSON
        config: Optional ToonConfig
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert
    if to_toon:
        data = json.loads(content)
        result = json_to_toon(data, config)
    else:
        data = toon_to_json(content, config)
        result = json.dumps(data, indent=2)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)


def get_conversion_stats(
    data: Any,
    config: Optional[ToonConfig] = None,
    output_format: str = "text"
) -> Dict[str, Any]:
    """
    Get statistics about JSON to TOON conversion.
    
    Args:
        data: Python data to analyze
        config: Optional ToonConfig
        output_format: Report format (text, json, markdown)
        
    Returns:
        Dictionary with conversion statistics
    """
    encoder = ToonEncoder(config or get_default_config())
    
    # Get JSON and TOON strings
    json_str = json.dumps(data, indent=2)
    toon_str = encoder.encode(data)
    
    # Get comparison
    comparison = compare_formats(data, encoder)
    
    # Generate report
    report = generate_report(comparison, output_format)
    
    return {
        "json_length": len(json_str),
        "toon_length": len(toon_str),
        "json_tokens": comparison.json_tokens,
        "toon_tokens": comparison.toon_tokens,
        "savings": comparison.savings,
        "savings_percent": comparison.savings_percent,
        "token_reduction": comparison.savings_percent,
        "report": report
    }
