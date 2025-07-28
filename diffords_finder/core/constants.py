"""Constants for DiffordsFinder."""

from typing import Dict

# Base configuration
BASE_URL: str = "https://www.diffordsguide.com"
DEFAULT_TIMEOUT: int = 10  # seconds
DEFAULT_DELAY: float = 1.0  # seconds between requests

# HTTP headers
HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Retry configuration
MAX_RETRIES: int = 3
RETRY_DELAY: float = 2.0  # seconds
RETRY_BACKOFF_FACTOR: float = 2.0

# Cache configuration
CACHE_DIR: str = ".diffords_cache"
CACHE_EXPIRY: int = 86400  # 24 hours in seconds

# Excel configuration
DEFAULT_SHEET_NAME: str = "Cocktails"
DEFAULT_COLUMN_NAME: str = "Name"
MAX_EXCEL_ROWS: int = 10000

# Search configuration
MAX_SEARCH_RESULTS: int = 10
FUZZY_MATCH_THRESHOLD: float = 0.8
INTERACTIVE_DISPLAY_BLOCK: int = 5

# Rate limiting
RATE_LIMIT_CALLS: int = 60
RATE_LIMIT_PERIOD: int = 60  # seconds

# Logging
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
