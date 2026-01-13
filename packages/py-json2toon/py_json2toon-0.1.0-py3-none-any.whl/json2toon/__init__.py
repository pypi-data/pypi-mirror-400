"""
json2toon - Convert JSON structures into TOON (Token-Oriented Object Notation)

A Python library for converting JSON to token-efficient TOON format,
optimized for LLM interactions.
"""

from .config import (
    ToonConfig,
    get_default_config,
    load_config,
    save_config
)
from .core import (
    convert_file,
    get_conversion_stats,
    json_to_toon,
    toon_to_json,
)
from .decoder import ToonDecoder
from .encoder import ToonEncoder
from .exceptions import (
    AnalysisError,
    ConfigurationError,
    DecodingError,
    EncodingError,
    Json2ToonError,
)
from .metrics import (
    ComparisonResult,
    compare_formats,
    count_tokens,
    generate_report
)
from .prompt import (
    create_llm_prompt,
    create_response_template,
    wrap_in_code_fence,
    add_system_prompt
)
from .analyzer import (
    StructureInfo,
    analyze_structure,
    is_uniform_array
)

__version__ = "0.1.0"
__all__ = [
    # Core functions
    "json_to_toon",
    "toon_to_json",
    "convert_file",
    "get_conversion_stats",
    # Classes
    "ToonEncoder",
    "ToonDecoder",
    "ToonConfig",
    "ComparisonResult",
    "StructureInfo",
    # Configuration
    "get_default_config",
    "load_config",
    "save_config",
    # Analysis
    "analyze_structure",
    "is_uniform_array",
    # Metrics
    "count_tokens",
    "compare_formats",
    "generate_report",
    # Prompts
    "create_llm_prompt",
    "create_response_template",
    "wrap_in_code_fence",
    "add_system_prompt",
    # Exceptions
    "Json2ToonError",
    "EncodingError",
    "DecodingError",
    "AnalysisError",
    "ConfigurationError",
]
