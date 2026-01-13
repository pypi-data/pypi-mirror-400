"""
JSON to TOON encoder.
"""
from typing import Any, Dict, List
from .config import ToonConfig, get_default_config
from .analyzer import should_use_table_format, is_uniform_array
from .exceptions import EncodingError


class ToonEncoder:
    """Encodes JSON data to TOON format."""
    
    def __init__(self, config: ToonConfig = None):
        """
        Initialize encoder.
        
        Args:
            config: Optional ToonConfig, uses defaults if not provided
        """
        self.config = config or get_default_config()
    
    def encode(self, data: Any, indent_level: int = 0) -> str:
        """
        Encode data to TOON format.
        
        Args:
            data: Data to encode
            indent_level: Current indentation level
            
        Returns:
            TOON-formatted string
            
        Raises:
            EncodingError: If encoding fails
        """
        try:
            return self._encode_value(data, indent_level)
        except Exception as e:
            raise EncodingError(f"Failed to encode data: {e}") from e
    
    def _looks_like_number(self, s: str) -> bool:
        """Check if a string looks like a number."""
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def _encode_value(self, data: Any, indent_level: int) -> str:
        """Encode a single value."""
        if data is None:
            return "null"
        elif isinstance(data, bool):
            return str(data).lower()
        elif isinstance(data, (int, float)):
            return str(data)
        elif isinstance(data, str):
            # Escape newlines and other special characters
            escaped = data.replace('\\', '\\\\').replace('\n', '\\n')
            # Quote if:
            # 1. Config requires it
            # 2. String has leading/trailing whitespace
            # 3. String looks like a number (to preserve string type)
            needs_quotes = (
                self.config.quote_strings or
                data != data.strip() or
                self._looks_like_number(data)
            )
            return f'"{escaped}"' if needs_quotes else escaped
        elif isinstance(data, list):
            return self._encode_array(data, indent_level)
        elif isinstance(data, dict):
            return self._encode_object(data, indent_level)
        else:
            return str(data)
    
    def _encode_array(self, arr: List[Any], indent_level: int) -> str:
        """Encode array to TOON format."""
        if not arr:
            return "[]"
        
        # Check if all items are arrays (deeply nested arrays)
        # Use inline JSON format for these
        if all(isinstance(item, list) for item in arr):
            import json
            return json.dumps(arr)
        
        # Check if we should use table format
        if should_use_table_format(arr, self.config):
            return self._encode_table(arr, indent_level)
        
        # Use inline format for short primitive arrays
        if (len(arr) <= self.config.max_inline_array_length and
                all(not isinstance(item, (dict, list))
                    for item in arr)):
            items = [self._encode_value(item, 0) for item in arr]
            return f"[{', '.join(items)}]"
        
        # Use indented list format
        child_indent = " " * ((indent_level + 1) * self.config.indent_size)
        
        lines = []
        for item in arr:
            if isinstance(item, dict):
                # For dict items, encode at level 0, add indent manually
                encoded = self._encode_value(item, 0)
                # Add dash to first line, indent rest
                item_lines = encoded.split('\n')
                lines.append(f"{child_indent}- {item_lines[0]}")
                extra_indent = " " * 2  # For continuation lines
                for line in item_lines[1:]:
                    lines.append(f"{child_indent}{extra_indent}{line}")
            else:
                encoded = self._encode_value(item, indent_level + 1)
                lines.append(f"{child_indent}- {encoded}")
        
        return "\n".join(lines)
    
    def _encode_table(
        self,
        arr: List[Dict[str, Any]],
        indent_level: int
    ) -> str:
        """Encode uniform array as table."""
        if not arr:
            return ""
        
        # Get common keys
        _, keys = is_uniform_array(arr, self.config.uniformity_threshold)
        
        if not keys:
            return self._encode_array(arr, indent_level)
        
        indent = " " * (indent_level * self.config.indent_size)
        sep = f" {self.config.table_separator} "
        table_sep = self.config.table_separator
        
        # Build header
        header = f"{indent}{table_sep}{sep.join(keys)}{sep}{table_sep}"
        
        # Build separator
        sep_line = f"{indent}{table_sep}"
        for _ in keys:
            header_sep = self.config.header_separator * 8
            sep_line += f"{header_sep}{table_sep}"
        
        # Build rows
        rows = [header, sep_line]
        for item in arr:
            row_values = []
            for key in keys:
                value = item.get(key, "")
                encoded = self._encode_value(value, 0)
                # Pad value for alignment
                row_values.append(f"{encoded:<8}")
            row = f"{indent}{table_sep}{sep.join(row_values)}{sep}{table_sep}"
            rows.append(row)
        
        return "\n".join(rows)
    
    def _encode_object(self, obj: Dict[str, Any], indent_level: int) -> str:
        """Encode object to TOON format."""
        if not obj:
            return "{}"
        
        indent = " " * (indent_level * self.config.indent_size)
        lines = []
        
        for key, value in obj.items():
            if isinstance(value, (dict, list)) and value:
                # Multi-line value
                lines.append(f"{indent}{key}{self.config.separator}")
                encoded = self._encode_value(value, indent_level + 1)
                # Check if encoded value needs indentation added
                # (inline arrays don't have indentation already)
                if isinstance(value, list) and not encoded.startswith(' '):
                    child_indent = " " * (
                        (indent_level + 1) * self.config.indent_size
                    )
                    encoded = child_indent + encoded
                lines.append(encoded)
            else:
                # Inline value
                encoded = self._encode_value(value, 0)
                lines.append(f"{indent}{key}{self.config.separator} {encoded}")
        
        return "\n".join(lines)
