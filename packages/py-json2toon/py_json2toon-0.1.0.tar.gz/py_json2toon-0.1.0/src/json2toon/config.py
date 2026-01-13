"""
Configuration module for json2toon library.
"""
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ToonConfig:
    """Configuration for TOON conversion behavior."""
    
    # Key-value formatting
    separator: str = ":"
    
    # Table formatting
    table_separator: str = "|"
    header_separator: str = "-"
    
    # Array handling
    max_inline_array_length: int = 10
    compress_primitive_arrays: bool = True
    
    # String handling
    max_string_length: Optional[int] = None
    quote_strings: bool = False
    
    # Nesting
    indent_size: int = 2
    max_nesting_depth: int = 10
    
    # Analysis
    uniformity_threshold: float = 0.8  # 80% of objects must match structure
    min_table_rows: int = 2  # Minimum rows to use table format


def get_default_config() -> ToonConfig:
    """Return default configuration."""
    return ToonConfig()


def save_config(config: ToonConfig, filepath: str) -> None:
    """Save configuration to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, indent=2)


def load_config(filepath: str) -> ToonConfig:
    """Load configuration from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return ToonConfig(**data)
