"""
Structure analyzer for json2toon library.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Optional
from .config import ToonConfig
from .exceptions import AnalysisError


@dataclass
class StructureInfo:
    """Information about JSON structure."""
    type: str  # 'object', 'array', 'primitive'
    is_uniform: bool  # For arrays: all items have same structure
    keys: Optional[List[str]] = None  # For uniform arrays: common keys
    item_count: Optional[int] = None  # For arrays: number of items



def is_uniform_array(
    arr: List[Dict[str, Any]],
    threshold: float = 0.8
) -> tuple[bool, List[str]]:
    """
    Check if array items have uniform structure.
    
    Args:
        arr: List of dictionaries
        threshold: Minimum key overlap ratio (0.0-1.0)
        
    Returns:
        Tuple of (is_uniform, common_keys)
    """
    if not arr or not all(isinstance(item, dict) for item in arr):
        return False, []
        
    
    # Collect all keys
    all_keys: Set[str] = set()
    for item in arr:
        all_keys.update(item.keys())
    
    if not all_keys:
        return False, []
    
    # Count key occurrences
    key_counts: Dict[str, int] = {key: 0 for key in all_keys}
    for item in arr:
        for key in item.keys():
            key_counts[key] += 1
    
    # Calculate uniformity
    total_items = len(arr)
    uniform_keys = [
        key for key, count in key_counts.items()
        if count / total_items >= threshold
    ]
    
    if all_keys:
        is_uniform = len(uniform_keys) / len(all_keys) >= threshold
    else:
        is_uniform = False
    
    return is_uniform, sorted(uniform_keys)


def should_use_table_format(data: Any, config: ToonConfig) -> bool:
    """
    Determine if data should use table format.
    
    Args:
        data: Data to analyze
        config: TOON configuration
        
    Returns:
        True if table format should be used
    """
    if not isinstance(data, list):
        return False
    
    if len(data) < config.min_table_rows:
        return False
    
    is_uniform, _ = is_uniform_array(data, config.uniformity_threshold)
    return is_uniform


def analyze_structure(data: Any, config: ToonConfig) -> StructureInfo:
    """
    Analyze data structure to determine encoding strategy.
    
    Args:
        data: Data to analyze
        config: TOON configuration
        
    Returns:
        StructureInfo object
        
    Raises:
        AnalysisError: If analysis fails
    """
    try:
        if isinstance(data, dict):
            return StructureInfo(
                type='object',
                is_uniform=False
            )
        elif isinstance(data, list):
            threshold = config.uniformity_threshold
            is_uniform, keys = is_uniform_array(data, threshold)
            return StructureInfo(
                type='array',
                is_uniform=is_uniform,
                keys=keys,
                item_count=len(data)
            )
        else:
            return StructureInfo(
                type='primitive',
                is_uniform=False
            )
    except Exception as e:
        raise AnalysisError(f"Failed to analyze structure: {e}") from e
