class DiffordsFinderError(Exception):
    """Base exception for all DiffordsFinder errors."""

    pass


class NetworkError(DiffordsFinderError):
    """Raised when network operations fail."""

    pass


class SearchError(DiffordsFinderError):
    """Raised when search operations fail."""

    pass


class ScrapingError(DiffordsFinderError):
    """Raised when scraping operations fail."""

    pass


class NoResultsError(SearchError):
    """Raised when no search results are found."""

    pass


class ParseError(ScrapingError):
    """Raised when HTML parsing fails."""

    pass


class RateLimitError(NetworkError):
    """Raised when rate limit is exceeded."""

    pass


class ValidationError(DiffordsFinderError):
    """Raised when input validation fails."""

    pass
