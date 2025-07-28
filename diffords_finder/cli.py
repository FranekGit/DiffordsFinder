from __future__ import annotations

import argparse
import json
import sys

from diffords_ingredients import scrape_ingredients
from diffords_search import search_recipe_url


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="diffords", description="Fetch cocktail ingredients from Difford’s Guide."
    )
    p.add_argument("query", help="Cocktail name to search for")
    p.add_argument(
        "-n",
        "--non-interactive",
        action="store_true",
        help="Do not prompt if the first search hit is not exact",
    )
    ns = p.parse_args(argv)

    url = search_recipe_url(
        ns.query,
        interactive=not ns.non_interactive,
    )
    if not url:
        sys.exit(1)

    data = scrape_ingredients(url)
    if data is None:
        sys.exit(2)

    print(json.dumps(data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
