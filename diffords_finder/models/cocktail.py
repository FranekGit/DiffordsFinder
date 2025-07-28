"""Data models for cocktail information."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Ingredient:
    """Represents a cocktail ingredient with its measurement."""

    name: str
    measure: str
    unit: str = ""

    def __str__(self) -> str:
        """Return a formatted string representation."""
        if self.unit:
            return f"{self.measure} {self.unit} {self.name}"
        return f"{self.measure} {self.name}"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"name": self.name, "measure": self.measure, "unit": self.unit}


@dataclass
class Cocktail:
    """Represents a complete cocktail recipe."""

    name: str
    url: str
    ingredients: list[Ingredient] = field(default_factory=list)
    search_query: Optional[str] = None
    match_confidence: float = 1.0
    scraped_at: Optional[datetime] = None

    def __post_init__(self):
        """Set scraped_at to current time if not provided."""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

    def add_ingredient(self, name: str, measure: str, unit: str = "") -> None:
        """Add an ingredient to the cocktail."""
        self.ingredients.append(Ingredient(name, measure, unit))

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary format for serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "ingredients": [ing.to_dict() for ing in self.ingredients],
            "search_query": self.search_query,
            "match_confidence": self.match_confidence,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }

    @classmethod
    def from_scraper_data(
        cls,
        name: str,
        url: str,
        ingredients_data: Dict[str, Dict[str, str]],
        search_query: Optional[str] = None,
        match_confidence: float = 1.0,
    ) -> Cocktail:
        """Create a Cocktail instance from scraper data format."""
        cocktail = cls(
            name=name,
            url=url,
            search_query=search_query,
            match_confidence=match_confidence,
        )

        for ingredient_name, data in ingredients_data.items():
            cocktail.add_ingredient(
                name=ingredient_name,
                measure=data.get("measure", ""),
                unit=data.get("unit", ""),
            )

        return cocktail


@dataclass
class SearchResult:
    """Represents a search result from Difford's Guide."""

    title: str
    url: str
    relevance_score: float = 1.0

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary format."""
        return {
            "title": self.title,
            "url": self.url,
            "relevance_score": self.relevance_score,
        }
