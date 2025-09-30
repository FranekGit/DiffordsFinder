# DiffordsFinder

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A powerful Python CLI tool for discovering and managing cocktail recipes from Difford's Guide. Search for cocktails, get detailed ingredient lists, and export recipes to various formats.

## Features

### Current Features
- **Smart Search**: Fuzzy matching to find cocktails even with typos
- **Multiple Output Formats**: JSON, Markdown, Table, Pretty, Simple, and Compact formats
- **Interactive Mode**: Choose from multiple matches when searching

## Installation

### From Source
```bash
git clone https://github.com/yourusername/diffords-finder.git
cd diffords-finder
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/diffords-finder.git
cd diffords-finder
pip install -e ".[dev]"
pre-commit install  # Install git hooks
```

## Quick Start

### Basic Usage

Search for a cocktail and display ingredients:
```bash
diffords mojito
```

### Output Formats

```bash
# Pretty format with numbering (default)
diffords "old fashioned" --format pretty

# Simple bullet list
diffords margarita --format simple

# Compact one-line format
diffords manhattan --format compact

# Table format
diffords "whiskey sour" --format table

# Markdown format
diffords negroni --format markdown

# JSON output for programmatic use
diffords martini --format json
```

### Save to File

```bash
# Save as JSON
diffords "mai tai" -o cocktail.json

# Save as text
diffords daiquiri --format markdown -o recipe.md
```

### Non-Interactive Mode

Skip the selection prompt and use best match:
```bash
diffords "gin fizz" --non-interactive
```


## Example Output

### Pretty Format (Default)
```
Mojito
=========

Ingredients:
   1. 2 oz      White rum
   2. 1 oz      Fresh lime juice
   3. 2 tsp     Sugar
   4. 6-8       Mint leaves
   5. Top       Soda water

Recipe URL: https://www.diffordsguide.com/cocktails/recipe/1376/mojito
```

### JSON Format
```json
{
    "name": "Mojito",
    "url": "https://www.diffordsguide.com/cocktails/recipe/1376/mojito",
    "search_query": "mojito",
    "match_confidence": 1.0,
    "ingredients": {
        "White rum": {"measure": "2", "unit": "oz"},
        "Fresh lime juice": {"measure": "1", "unit": "oz"},
        "Sugar": {"measure": "2", "unit": "tsp"},
        "Mint leaves": {"measure": "6-8", "unit": ""},
        "Soda water": {"measure": "Top", "unit": ""}
    }
}
```

## Configuration

### Environment Variables
```bash
# Set logging level
export DIFFORDS_LOG_LEVEL=DEBUG

# Set default output format
export DIFFORDS_DEFAULT_FORMAT=markdown

# Set request timeout (seconds)
export DIFFORDS_TIMEOUT=15
```

### Custom Headers and Rate Limiting
The tool respects rate limiting and uses polite scraping practices by default. You can adjust the delay between requests:

```python
from diffords_finder.core import CocktailScraper

scraper = CocktailScraper(delay=2.0)  # 2 seconds between requests
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal use only. Please respect Difford's Guide's terms of service and robots.txt file. The tool implements rate limiting and polite scraping practices by default. Always attribute recipes to Difford's Guide when sharing.

## Acknowledgments

- [Difford's Guide](https://www.diffordsguide.com/) for their comprehensive cocktail database

