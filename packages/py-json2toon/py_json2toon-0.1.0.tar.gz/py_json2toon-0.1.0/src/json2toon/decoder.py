"""
TOON to JSON decoder.
"""
from typing import Any, Dict, List
from .config import ToonConfig, get_default_config
from .exceptions import DecodingError


class ToonDecoder:
    """Decodes TOON format to JSON data."""
    
    def __init__(self, config: ToonConfig = None):
        """
        Initialize decoder.
        
        Args:
            config: Optional ToonConfig, uses defaults if not provided
        """
        self.config = config or get_default_config()
    
    def decode(self, toon_str: str) -> Any:
        """
        Decode TOON string to Python data.
        
        Args:
            toon_str: TOON-formatted string
            
        Returns:
            Decoded Python data
            
        Raises:
            DecodingError: If decoding fails
        """
        try:
            lines = toon_str.strip().split('\n')
            result, _ = self._parse_value(lines, 0)
            return result
        except Exception as e:
            raise DecodingError(f"Failed to decode TOON: {e}") from e
    
    def _parse_value(self, lines: List[str], line_idx: int) -> tuple[Any, int]:
        """Parse a value and return (value, next_line_index)."""
        if line_idx >= len(lines):
            return None, line_idx
        
        line = lines[line_idx]
        stripped = line.lstrip()
        
        # Check if it's a list (starts with -)
        if stripped.startswith('- '):
            return self._parse_list(lines, line_idx)
        
        # Check if it's a table
        if self.config.table_separator in line:
            return self._parse_table(lines, line_idx)
        
        # Check if it's an object (key<separator> value)
        if self.config.separator in line:
            return self._parse_object(lines, line_idx)
        
        # Otherwise it's a primitive
        return self._parse_primitive(line.strip()), line_idx + 1
    
    def _parse_primitive(self, value_str: str) -> Any:
        """Parse primitive value."""
        value_str = value_str.strip()
        
        if value_str == "null":
            return None
        elif value_str == "true":
            return True
        elif value_str == "false":
            return False
        
        # Try parsing as JSON array or object
        if (value_str.startswith('[') and value_str.endswith(']')) or \
           (value_str.startswith('{') and value_str.endswith('}')):
            try:
                import json
                return json.loads(value_str)
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, try parsing as unquoted array
                if value_str.startswith('[') and value_str.endswith(']'):
                    content = value_str[1:-1].strip()
                    if not content:
                        return []
                    # Split by comma and parse each item
                    items = [
                        self._parse_primitive(item.strip())
                        for item in content.split(',')
                    ]
                    return items
        
        # Try parsing as number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Remove quotes if present
        if value_str.startswith('"') and value_str.endswith('"'):
            value_str = value_str[1:-1]
        
        # Unescape special characters (reverse order of encoding)
        # First replace escaped backslashes, then escaped newlines
        value_str = value_str.replace('\\\\', '\x00')  # Temp marker
        value_str = value_str.replace('\\n', '\n')
        value_str = value_str.replace('\x00', '\\')  # Restore backslashes
        
        return value_str
    
    def _parse_list(
        self,
        lines: List[str],
        line_idx: int
    ) -> tuple[List, int]:
        """Parse list format (dash-prefixed items)."""
        result = []
        base_line = lines[line_idx]
        base_indent = len(base_line) - len(base_line.lstrip())
        
        while line_idx < len(lines):
            line = lines[line_idx]
            stripped = line.lstrip()
            line_indent = len(line) - len(line.lstrip())
            
            # Stop if we've outdented or line doesn't start with -
            if line.strip() and (
                line_indent < base_indent or
                (line_indent == base_indent and not stripped.startswith('- '))
            ):
                break
            
            # Skip empty lines
            if not line.strip():
                line_idx += 1
                continue
            
            if stripped.startswith('- '):
                # Extract content after dash
                content = stripped[2:].strip()
                
                if self.config.separator in content:
                    # It's a dict item
                    # Parse as object starting from current line
                    # but with dash removed
                    modified_lines = lines.copy()
                    modified_lines[line_idx] = ' ' * line_indent + content
                    obj, next_idx = self._parse_object(
                        modified_lines, line_idx
                    )
                    result.append(obj)
                    line_idx = next_idx
                else:
                    # It's a primitive
                    result.append(self._parse_primitive(content))
                    line_idx += 1
            else:
                line_idx += 1
        
        return result, line_idx

    def _parse_table(
        self,
        lines: List[str],
        line_idx: int
    ) -> tuple[List[Dict], int]:
        """Parse table format."""
        sep = self.config.table_separator
        
        # Parse header
        header_line = lines[line_idx].strip()
        if not header_line.startswith(sep):
            raise DecodingError(f"Invalid table header at line {line_idx}")
        
        # Extract column names (filter out empty strings)
        cols = [
            col.strip() for col in header_line.strip(sep).split(sep)
            if col.strip()
        ]
        
        # Skip separator line
        line_idx += 2
        
        # Parse rows
        rows = []
        while line_idx < len(lines):
            line = lines[line_idx].strip()
            
            # Stop if not a table row
            if not line.startswith(sep):
                break
            
            # Extract values (filter out empty strings)
            values = [
                val.strip() for val in line.strip(sep).split(sep)
                if val.strip()
            ]
            
            # Build dictionary
            row_dict = {}
            for i, col in enumerate(cols):
                if i < len(values):
                    row_dict[col] = self._parse_primitive(values[i])
            
            rows.append(row_dict)
            line_idx += 1
        
        return rows, line_idx
    
    def _parse_object(
        self,
        lines: List[str],
        line_idx: int
    ) -> tuple[Dict, int]:
        """Parse object format."""
        obj = {}
        base_line = lines[line_idx]
        base_indent = len(base_line) - len(base_line.lstrip())
        
        while line_idx < len(lines):
            line = lines[line_idx]
            line_indent = len(line) - len(line.lstrip())
            
            # Stop if we've outdented
            if line.strip() and line_indent < base_indent:
                break
            
            # Skip empty lines
            if not line.strip():
                line_idx += 1
                continue
            
            # Parse key-value pair
            if self.config.separator in line:
                key, _, value = line.partition(self.config.separator)
                key = key.strip()
                value = value.strip()
                
                if not value:
                    # Check if next line is a multi-line value or another key
                    line_idx += 1
                    if line_idx < len(lines):
                        next_line = lines[line_idx]
                        # Calculate indentation levels
                        next_indent = (
                            len(next_line) - len(next_line.lstrip())
                        )
                        # If next line is not indented more, it's empty value
                        if (not next_line.strip() or
                                next_indent <= line_indent):
                            obj[key] = ""
                        else:
                            # Next line is more indented, parse as child
                            parsed_value, line_idx = self._parse_value(
                                lines, line_idx
                            )
                            obj[key] = parsed_value
                    else:
                        # End of file, empty value
                        obj[key] = ""
                else:
                    # Inline value
                    obj[key] = self._parse_primitive(value)
                    line_idx += 1
            else:
                line_idx += 1
        
        return obj, line_idx

