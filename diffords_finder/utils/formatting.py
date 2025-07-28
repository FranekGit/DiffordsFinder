"""Formatting utilities for cocktail display."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.cocktail import Cocktail


def format_ingredients_pretty(cocktail: Cocktail) -> str:
    """
    Format ingredients as a pretty list with emojis and numbering.

    Args:
        cocktail: Cocktail object with ingredients

    Returns:
        Formatted string with ingredients list
    """
    lines = []
    lines.append(f"{cocktail.name}")
    lines.append("=" * (len(cocktail.name) + 3))
    lines.append("")

    if cocktail.ingredients:
        lines.append("Ingredients:")

        # Calculate max width for alignment
        max_measure_width = 0
        for ingredient in cocktail.ingredients:
            if ingredient.unit:
                measure_text = f"{ingredient.measure} {ingredient.unit}"
            else:
                measure_text = ingredient.measure
            max_measure_width = max(max_measure_width, len(measure_text))

        # Format each ingredient with alignment
        for i, ingredient in enumerate(cocktail.ingredients, 1):
            if ingredient.unit:
                measure_text = f"{ingredient.measure} {ingredient.unit}"
            else:
                measure_text = ingredient.measure

            lines.append(
                f"  {i:2d}. {measure_text:<{max_measure_width}} {ingredient.name}"
            )
    else:
        lines.append("No ingredients found.")

    lines.append("")
    lines.append(f"Recipe URL: {cocktail.url}")

    return "\n".join(lines)


def format_ingredients_simple(cocktail: Cocktail) -> str:
    """
    Format ingredients as a clean list without extra formatting.

    Args:
        cocktail: Cocktail object with ingredients

    Returns:
        Simple formatted string
    """
    lines = []
    lines.append(cocktail.name)
    lines.append("-" * len(cocktail.name))
    lines.append("")

    if cocktail.ingredients:
        for ingredient in cocktail.ingredients:
            if ingredient.unit:
                measure_text = f"{ingredient.measure} {ingredient.unit}"
            else:
                measure_text = ingredient.measure
            lines.append(f"• {measure_text} {ingredient.name}")
    else:
        lines.append("No ingredients found.")

    return "\n".join(lines)


def format_ingredients_compact(cocktail: Cocktail) -> str:
    """
    Format ingredients in a compact single-line format.

    Args:
        cocktail: Cocktail object with ingredients

    Returns:
        Compact formatted string
    """
    if not cocktail.ingredients:
        return f"{cocktail.name}: No ingredients found"

    ingredient_parts = []
    for ingredient in cocktail.ingredients:
        if ingredient.unit:
            measure_text = f"{ingredient.measure} {ingredient.unit}"
        else:
            measure_text = ingredient.measure
        ingredient_parts.append(f"{measure_text} {ingredient.name}")

    return f"{cocktail.name}: {', '.join(ingredient_parts)}"


def format_ingredients_table(cocktail: Cocktail) -> str:
    """
    Format ingredients as a table-like structure.

    Args:
        cocktail: Cocktail object with ingredients

    Returns:
        Table formatted string
    """
    lines = []
    lines.append(f"Cocktail: {cocktail.name}")
    lines.append("")

    if not cocktail.ingredients:
        lines.append("No ingredients found.")
        return "\n".join(lines)

    # Calculate column widths
    max_measure_width = max(
        len(f"{ing.measure} {ing.unit}".strip()) for ing in cocktail.ingredients
    )
    max_name_width = max(len(ing.name) for ing in cocktail.ingredients)

    # Ensure minimum widths
    max_measure_width = max(max_measure_width, 8)  # "Measure"
    max_name_width = max(max_name_width, 10)  # "Ingredient"

    # Table header
    lines.append(f"{'Measure':<{max_measure_width}} | {'Ingredient':<{max_name_width}}")
    lines.append(f"{'-' * max_measure_width}-+-{'-' * max_name_width}")

    # Table rows
    for ingredient in cocktail.ingredients:
        if ingredient.unit:
            measure_text = f"{ingredient.measure} {ingredient.unit}"
        else:
            measure_text = ingredient.measure

        lines.append(
            f"{measure_text:<{max_measure_width}} | {ingredient.name:<{max_name_width}}"
        )

    return "\n".join(lines)


def format_ingredients_markdown(cocktail: Cocktail) -> str:
    """
    Format ingredients as Markdown.

    Args:
        cocktail: Cocktail object with ingredients

    Returns:
        Markdown formatted string
    """
    lines = []
    lines.append(f"# {cocktail.name}")
    lines.append("")

    if cocktail.ingredients:
        lines.append("## Ingredients")
        lines.append("")
        for ingredient in cocktail.ingredients:
            if ingredient.unit:
                measure_text = f"{ingredient.measure} {ingredient.unit}"
            else:
                measure_text = ingredient.measure
            lines.append(f"- **{measure_text}** {ingredient.name}")
    else:
        lines.append("*No ingredients found.*")

    lines.append("")
    lines.append(f"**Source:** [{cocktail.url}]({cocktail.url})")

    if cocktail.match_confidence < 1.0:
        confidence_pct = cocktail.match_confidence * 100
        lines.append(f"**Match confidence:** {confidence_pct:.0f}%")

    return "\n".join(lines)


# Mapping of format names to functions
FORMAT_FUNCTIONS = {
    "pretty": format_ingredients_pretty,
    "simple": format_ingredients_simple,
    "compact": format_ingredients_compact,
    "table": format_ingredients_table,
    "markdown": format_ingredients_markdown,
}


def get_available_formats() -> list[str]:
    """Get list of available format names."""
    return list(FORMAT_FUNCTIONS.keys())


def format_cocktail(cocktail: Cocktail, format_name: str) -> str:
    """
    Format a cocktail using the specified format.

    Args:
        cocktail: Cocktail object to format
        format_name: Name of the format to use

    Returns:
        Formatted string

    Raises:
        ValueError: If format_name is not recognized
    """
    format_func = FORMAT_FUNCTIONS.get(format_name.lower())
    if not format_func:
        available = ", ".join(get_available_formats())
        raise ValueError(
            f"Unknown format '{format_name}'. Available formats: {available}"
        )

    return format_func(cocktail)
