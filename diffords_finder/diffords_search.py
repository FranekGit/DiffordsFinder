from __future__ import annotations

import sys
import urllib.parse
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from constants import BASE_URL, DEFAULT_TIMEOUT, HEADERS


def _extract_recipe_links(soup: BeautifulSoup) -> list[BeautifulSoup]:
    """Return *unique* <a> tags that point to recipe pages."""
    raw_links = soup.select('a[href*="/cocktails/recipe/"]')
    seen: set[str] = set()
    out: list[BeautifulSoup] = []
    for a in raw_links:
        href = a["href"]
        if href not in seen:
            seen.add(href)
            out.append(a)
    return out


def _pick_link_interactively(
    links: list[BeautifulSoup], display_block: int = 3, stream=sys.stderr
) -> BeautifulSoup | None:
    """Let the user pick one link from *links* or cancel."""

    def link_title(a_tag: BeautifulSoup) -> str:
        return a_tag.get_text(strip=True)

    displayed = 0
    mapping: dict[int, BeautifulSoup] = {}

    while True:
        batch = links[displayed : displayed + display_block]
        if not batch:
            print("⭑ No more matches.", file=stream)
            return None
        for i, a in enumerate(batch, start=displayed + 1):
            mapping[i] = a
            print(f"  {i}. {link_title(a)}", file=stream)
        displayed += len(batch)

        choice = (
            input(
                "Pick a number, or type “m” for more, or just press Enter to cancel: "
            )
            .strip()
            .lower()
        )
        if not choice:
            return None
        if choice in {"m", "more"}:
            continue
        try:
            idx = int(choice)
            if idx in mapping:
                return mapping[idx]
            print("Invalid number. Try again.", file=stream)
        except ValueError:
            print("Invalid input. Try again.", file=stream)


def search_recipe_url(
    cocktail_name: str,
    *,
    interactive: bool = True,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str | None:
    """
    Return the absolute recipe URL for *cocktail_name*.

    If *interactive* is True and the first hit is not an exact match,
    the user can choose from further hits.  Returns None on failure or cancel.
    """
    sess = session or requests
    search_q = urllib.parse.quote_plus(cocktail_name)
    url = f"{BASE_URL}/search?q={search_q}"

    try:
        resp = sess.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[network] search failed: {exc}", file=sys.stderr)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    links = _extract_recipe_links(soup)
    if not links:
        print(f"No recipes found for “{cocktail_name}”.", file=sys.stderr)
        return None

    exact_wanted = cocktail_name.strip().lower()
    first_title = links[0].get_text(strip=True).lower()

    chosen = (
        _pick_link_interactively(links)
        if interactive and first_title != exact_wanted
        else links[0]
    )

    return BASE_URL + chosen["href"] if chosen else None
