"""Enhanced search functionality for Difford's Guide."""

from __future__ import annotations

import urllib.parse
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from ..models.cocktail import SearchResult
from ..utils.exceptions import NetworkError, NoResultsError, SearchError
from ..utils.logger import logger
from .constants import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    FUZZY_MATCH_THRESHOLD,
    HEADERS,
    INTERACTIVE_DISPLAY_BLOCK,
    MAX_SEARCH_RESULTS,
)


class CocktailSearcher:
    """Search for cocktails on Difford's Guide."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_results: int = MAX_SEARCH_RESULTS,
    ):
        """
        Initialize the searcher.

        Args:
            session: Optional requests session
            timeout: Request timeout in seconds
            max_results: Maximum number of results to return
        """
        self.session = session or requests.Session()
        self.session.headers.update(HEADERS)
        self.timeout = timeout
        self.max_results = max_results

    def search(self, cocktail_name: str) -> List[SearchResult]:
        """
        Search for cocktails by name.

        Args:
            cocktail_name: Name of the cocktail to search for

        Returns:
            List of search results

        Raises:
            SearchError: If search fails
            NoResultsError: If no results found
        """
        logger.info(f"Searching for cocktail: {cocktail_name}")

        # Build search URL
        search_query = urllib.parse.quote_plus(cocktail_name)
        search_url = f"{BASE_URL}/search?q={search_query}"

        try:
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Search request failed: {exc}")
            raise NetworkError(f"Search request failed: {exc}")

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            results = self._extract_search_results(soup, cocktail_name)

            if not results:
                raise NoResultsError(f"No cocktails found for '{cocktail_name}'")

            logger.info(f"Found {len(results)} results for '{cocktail_name}'")
            return results[: self.max_results]

        except Exception as exc:
            if isinstance(exc, NoResultsError):
                raise
            logger.error(f"Failed to parse search results: {exc}")
            raise SearchError(f"Failed to parse search results: {exc}")

    def _extract_search_results(
        self, soup: BeautifulSoup, query: str
    ) -> List[SearchResult]:
        """
        Extract search results from the page.

        Args:
            soup: BeautifulSoup object of the search page
            query: Original search query for relevance scoring

        Returns:
            List of search results with relevance scores
        """
        results = []
        seen_urls = set()

        # Find all recipe links
        recipe_links = soup.select('a[href*="/cocktails/recipe/"]')

        for link in recipe_links:
            href = link.get("href", "")
            if not href or href in seen_urls:
                continue

            seen_urls.add(href)

            # Extract title
            title = link.get_text(strip=True)
            if not title:
                # Try to find title in parent or child elements
                title_elem = link.find(["h2", "h3", "h4", "span", "div"])
                if title_elem:
                    title = title_elem.get_text(strip=True)

            if not title:
                continue

            # Calculate relevance score
            relevance_score = self._calculate_relevance(title, query)

            # Build full URL
            full_url = href if href.startswith("http") else BASE_URL + href

            results.append(
                SearchResult(title=title, url=full_url, relevance_score=relevance_score)
            )

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results

    def _calculate_relevance(self, title: str, query: str) -> float:
        """
        Calculate relevance score between title and query.

        Args:
            title: Cocktail title
            query: Search query

        Returns:
            Relevance score between 0 and 1
        """
        # Normalize strings
        title_lower = title.lower().strip()
        query_lower = query.lower().strip()

        # Exact match
        if title_lower == query_lower:
            return 1.0

        # Use fuzzy matching
        ratio = fuzz.ratio(query_lower, title_lower) / 100.0
        partial_ratio = fuzz.partial_ratio(query_lower, title_lower) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(query_lower, title_lower) / 100.0

        # Weighted average
        return ratio * 0.4 + partial_ratio * 0.3 + token_sort_ratio * 0.3

    def find_best_match(self, cocktail_name: str) -> Optional[SearchResult]:
        """
        Find the best matching cocktail for the given name.

        Args:
            cocktail_name: Name of the cocktail

        Returns:
            Best matching SearchResult or None if no good match
        """
        try:
            results = self.search(cocktail_name)
        except NoResultsError:
            return None

        if not results:
            return None

        # Check if the best match is good enough
        best_match = results[0]
        if best_match.relevance_score >= FUZZY_MATCH_THRESHOLD:
            return best_match

        return None

    def interactive_search(
        self, cocktail_name: str, display_block: int = INTERACTIVE_DISPLAY_BLOCK
    ) -> Optional[SearchResult]:
        """
        Perform an interactive search where user can choose from results.

        Args:
            cocktail_name: Name of the cocktail
            display_block: Number of results to display at once

        Returns:
            Selected SearchResult or None if cancelled
        """
        try:
            results = self.search(cocktail_name)
        except NoResultsError:
            print(f"No cocktails found for '{cocktail_name}'")
            return None

        # Check for exact match first
        exact_match = None
        for result in results:
            if result.title.lower().strip() == cocktail_name.lower().strip():
                exact_match = result
                break

        if exact_match:
            return exact_match

        # Interactive selection
        print(f"\nMultiple cocktails found for '{cocktail_name}':")
        return self._interactive_select(results, display_block)

    def _interactive_select(
        self, results: List[SearchResult], display_block: int
    ) -> Optional[SearchResult]:
        """
        Let user interactively select from search results.

        Args:
            results: List of search results
            display_block: Number of results to show at once

        Returns:
            Selected result or None if cancelled
        """
        displayed = 0
        total = len(results)

        while displayed < total:
            # Display batch
            batch_end = min(displayed + display_block, total)
            print(f"\nShowing results {displayed + 1}-{batch_end} of {total}:")

            for i in range(displayed, batch_end):
                result = results[i]
                confidence = f"({result.relevance_score:.0%} match)"
                print(f"  {i + 1}. {result.title} {confidence}")

            displayed = batch_end

            # Get user input
            if displayed < total:
                prompt = "\nEnter number to select, 'm' for more, or Enter to cancel: "
            else:
                prompt = "\nEnter number to select, or Enter to cancel: "

            choice = input(prompt).strip().lower()

            # Process choice
            if not choice:
                return None

            if choice == "m" and displayed < total:
                continue

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    return results[idx]
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'm' for more.")

        return None

    def close(self) -> None:
        """Close the session."""
        if hasattr(self, "session") and self.session:
            self.session.close()


def search_cocktail_url(
    cocktail_name: str,
    interactive: bool = True,
    session: Optional[requests.Session] = None,
) -> Optional[Tuple[str, float]]:
    """
    Legacy function for backward compatibility.

    Args:
        cocktail_name: Name of the cocktail
        interactive: Whether to use interactive mode
        session: Optional requests session

    Returns:
        Tuple of (URL, confidence_score) or None
    """
    searcher = CocktailSearcher(session=session)

    try:
        if interactive:
            result = searcher.interactive_search(cocktail_name)
        else:
            result = searcher.find_best_match(cocktail_name)

        if result:
            return result.url, result.relevance_score
        return None

    finally:
        searcher.close()
