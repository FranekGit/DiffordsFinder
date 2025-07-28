"""Simple CLI for finding cocktail ingredients."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import click

from ..core.scraper import CocktailScraper
from ..core.search import CocktailSearcher
from ..utils.exceptions import DiffordsFinderError, NoResultsError
from ..utils.logger import setup_logger


@click.command()
@click.argument("query")
@click.option(
    "-n",
    "--non-interactive",
    is_flag=True,
    help="Do not prompt if the first search hit is not exact",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file (JSON format). If not specified, prints to stdout",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option("--timeout", type=int, default=10, help="Request timeout in seconds")
def main(
    query: str,
    non_interactive: bool,
    output: Path | None,
    verbose: bool,
    pretty: bool,
    timeout: int,
) -> None:
    """
    Search for a cocktail recipe on Difford's Guide.

    QUERY: Name of the cocktail to search for
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "WARNING"
    logger = setup_logger(level=log_level)

    # Create searcher and scraper
    searcher = CocktailSearcher(timeout=timeout)
    scraper = CocktailScraper(timeout=timeout)

    try:
        # Search for cocktail
        if non_interactive:
            result = searcher.find_best_match(query)
            if not result:
                click.echo(f"No good match found for '{query}'", err=True)
                sys.exit(1)
        else:
            result = searcher.interactive_search(query)
            if not result:
                click.echo("Search cancelled", err=True)
                sys.exit(1)

        # Log the match confidence
        if verbose:
            click.echo(
                f"Found: {result.title} (confidence: {result.relevance_score:.0%})",
                err=True,
            )

        # Scrape the cocktail
        cocktail = scraper.scrape_cocktail(
            recipe_url=result.url,
            cocktail_name=result.title,
            search_query=query,
            match_confidence=result.relevance_score,
        )

        # Prepare output data
        output_data = {
            "name": cocktail.name,
            "url": cocktail.url,
            "search_query": cocktail.search_query,
            "match_confidence": cocktail.match_confidence,
            "ingredients": {
                ing.name: {"measure": ing.measure, "unit": ing.unit}
                for ing in cocktail.ingredients
            },
        }

        # Format JSON
        json_output = json.dumps(
            output_data, indent=4 if pretty else None, ensure_ascii=False
        )

        # Output results
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json_output, encoding="utf-8")
            click.echo(f"Results saved to: {output}")
        else:
            click.echo(json_output)

    except NoResultsError:
        click.echo(f"No cocktails found for '{query}'", err=True)
        sys.exit(1)

    except DiffordsFinderError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    except KeyboardInterrupt:
        click.echo("\nSearch cancelled by user", err=True)
        sys.exit(130)

    except Exception as exc:
        logger.exception("Unexpected error occurred")
        click.echo(f"Unexpected error: {exc}", err=True)
        sys.exit(3)

    finally:
        searcher.close()
        scraper.close()


# Legacy entry point for backward compatibility
def legacy_main(argv: list[str] | None = None) -> None:
    """Legacy argparse-based entry point."""
    parser = argparse.ArgumentParser(
        prog="diffords", description="Fetch cocktail ingredients from Difford's Guide."
    )
    parser.add_argument("query", help="Cocktail name to search for")
    parser.add_argument(
        "-n",
        "--non-interactive",
        action="store_true",
        help="Do not prompt if the first search hit is not exact",
    )

    args = parser.parse_args(argv)

    # Convert to click command
    ctx = click.Context(main)
    ctx.invoke(main, query=args.query, non_interactive=args.non_interactive)


if __name__ == "__main__":
    main()
