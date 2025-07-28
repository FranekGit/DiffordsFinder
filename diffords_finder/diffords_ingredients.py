from __future__ import annotations

import sys

import requests
from bs4 import BeautifulSoup
from constants import DEFAULT_TIMEOUT, HEADERS


def scrape_ingredients(
    recipe_url: str,
    *,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, dict[str, str]] | None:
    """
    Return {ingredient: {"measure": ..., "unit": ...}, ...}
    or None on failure.
    """
    sess = session or requests
    try:
        resp = sess.get(recipe_url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[network] recipe fetch failed: {exc}", file=sys.stderr)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", class_="legacy-ingredients-table")
    if not table:
        print("Could not locate the ingredients table.", file=sys.stderr)
        return None

    out: dict[str, dict[str, str]] = {}
    for row in table.tbody.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) != 2:
            continue
        qty = tds[0].get_text(strip=True)
        name = tds[1].get_text(strip=True)

        measure, _, unit = qty.partition(" ")
        out[name] = {"measure": measure, "unit": unit}

    return out
