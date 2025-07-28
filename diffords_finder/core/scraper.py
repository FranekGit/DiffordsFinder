from __future__ import annotations

import time
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from ..models.cocktail import Cocktail
from ..utils.exceptions import NetworkError, ParseError, ScrapingError
from ..utils.logger import logger
from .constants import DEFAULT_DELAY, DEFAULT_TIMEOUT, HEADERS, MAX_RETRIES, RETRY_DELAY


class CocktailScraper:
    """Scraper for extracting cocktail ingredients from Difford's Guide."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        delay: float = DEFAULT_DELAY,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize the scraper.

        Args:
            session: Optional requests session for connection pooling
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts
        """
        self.session = session or requests.Session()
        self.session.headers.update(HEADERS)
        self.timeout = timeout
        self.delay = delay
        self.max_retries = max_retries
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Implement rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _fetch_page(self, url: str) -> str:
        """
        Fetch a page with retry logic.

        Args:
            url: URL to fetch

        Returns:
            Page HTML content

        Raises:
            NetworkError: If all retry attempts fail
        """
        self._rate_limit()

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Fetching URL: {url} (attempt {attempt + 1}/{self.max_retries})"
                )
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                logger.info(f"Successfully fetched: {url}")
                return response.text

            except requests.exceptions.RequestException as exc:
                last_error = exc
                logger.warning(f"Request failed (attempt {attempt + 1}): {exc}")

                if attempt < self.max_retries - 1:
                    sleep_time = RETRY_DELAY * (2**attempt)  # Exponential backoff
                    logger.debug(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        raise NetworkError(
            f"Failed to fetch {url} after {self.max_retries} attempts: {last_error}"
        )

    def scrape_cocktail(
        self,
        recipe_url: str,
        cocktail_name: Optional[str] = None,
        search_query: Optional[str] = None,
        match_confidence: float = 1.0,
    ) -> Cocktail:
        """
        Scrape a cocktail recipe from its URL.

        Args:
            recipe_url: URL of the cocktail recipe
            cocktail_name: Optional cocktail name (will be extracted if not provided)
            search_query: Original search query
            match_confidence: Confidence score of the match

        Returns:
            Cocktail object with ingredients

        Raises:
            ScrapingError: If scraping fails
        """
        try:
            html = self._fetch_page(recipe_url)
        except NetworkError as exc:
            raise ScrapingError(f"Failed to fetch recipe page: {exc}")

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Extract cocktail name if not provided
            if not cocktail_name:
                name_elem = soup.find("h1", class_="recipe-name")
                if name_elem:
                    cocktail_name = name_elem.get_text(strip=True)
                else:
                    # Fallback: try to extract from title
                    title_elem = soup.find("title")
                    if title_elem:
                        cocktail_name = title_elem.get_text(strip=True).split(" - ")[0]
                    else:
                        cocktail_name = "Unknown Cocktail"

            # Find ingredients table
            table = soup.find("table", class_="legacy-ingredients-table")
            if not table:
                # Try alternative selectors
                table = soup.find("table", {"id": "ingredients-table"})
                if not table:
                    table = soup.find("div", class_="recipe-ingredients")

            if not table:
                raise ParseError("Could not locate ingredients table")

            # Extract ingredients
            ingredients_data = self._parse_ingredients_table(table)

            # Create cocktail object
            cocktail = Cocktail.from_scraper_data(
                name=cocktail_name,
                url=recipe_url,
                ingredients_data=ingredients_data,
                search_query=search_query,
                match_confidence=match_confidence,
            )

            logger.info(
                f"Successfully scraped cocktail: {cocktail_name} with {len(cocktail.ingredients)} ingredients"
            )
            return cocktail

        except Exception as exc:
            logger.error(f"Failed to parse cocktail page: {exc}")
            raise ScrapingError(f"Failed to parse cocktail information: {exc}")

    def _parse_ingredients_table(self, table_elem) -> Dict[str, Dict[str, str]]:
        """
        Parse ingredients from table element.

        Args:
            table_elem: BeautifulSoup table element

        Returns:
            Dictionary of ingredients with measures and units
        """
        ingredients = {}

        # Handle table format
        if table_elem.name == "table":
            tbody = table_elem.find("tbody") or table_elem
            for row in tbody.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    quantity = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)

                    # Parse quantity into measure and unit
                    measure, unit = self._parse_quantity(quantity)
                    ingredients[name] = {"measure": measure, "unit": unit}

        # Handle div format (alternative layout)
        elif table_elem.name == "div":
            for item in table_elem.find_all(
                ["div", "li"], class_=["ingredient", "recipe-ingredient"]
            ):
                # Try to find quantity and name elements
                qty_elem = item.find(class_=["quantity", "ingredient-quantity"])
                name_elem = item.find(class_=["name", "ingredient-name"])

                if qty_elem and name_elem:
                    quantity = qty_elem.get_text(strip=True)
                    name = name_elem.get_text(strip=True)
                    measure, unit = self._parse_quantity(quantity)
                    ingredients[name] = {"measure": measure, "unit": unit}

        return ingredients

    def _parse_quantity(self, quantity: str) -> tuple[str, str]:
        """
        Parse quantity string into measure and unit.

        Args:
            quantity: Quantity string (e.g., "2 oz", "1.5 ml", "3 dashes")

        Returns:
            Tuple of (measure, unit)
        """
        parts = quantity.strip().split(maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return "", ""

    def close(self) -> None:
        """Close the session."""
        if hasattr(self, "session") and self.session:
            self.session.close()
