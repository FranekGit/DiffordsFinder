"""Utility modules for DiffordsFinder."""

from .exceptions import (
    DiffordsFinderError,
    NetworkError,
    NoResultsError,
    ParseError,
    RateLimitError,
    ScrapingError,
    SearchError,
    ValidationError,
)
from .formatting import (
    FORMAT_FUNCTIONS,
    format_cocktail,
    format_ingredients_compact,
    format_ingredients_markdown,
    format_ingredients_pretty,
    format_ingredients_simple,
    format_ingredients_table,
    get_available_formats,
)
from .logger import logger, setup_logger

__all__ = [
    "DiffordsFinderError",
    "NetworkError",
    "NoResultsError",
    "ParseError",
    "RateLimitError",
    "ScrapingError",
    "SearchError",
    "ValidationError",
    "logger",
    "setup_logger",
    "FORMAT_FUNCTIONS",
    "format_cocktail",
    "format_ingredients_compact",
    "format_ingredients_markdown",
    "format_ingredients_pretty",
    "format_ingredients_simple",
    "format_ingredients_table",
    "get_available_formats",
]
