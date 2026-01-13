"""
Custom exceptions for json2toon library.
"""


class Json2ToonError(Exception):
    """Base exception for json2toon library."""
    pass


class EncodingError(Json2ToonError):
    """Raised when JSON to TOON encoding fails."""
    pass


class DecodingError(Json2ToonError):
    """Raised when TOON to JSON decoding fails."""
    pass


class AnalysisError(Json2ToonError):
    """Raised when structure analysis fails."""
    pass


class ConfigurationError(Json2ToonError):
    """Raised when configuration is invalid."""
    pass
