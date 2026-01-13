"""
Data models for EasyLCSC4KiCAD.

Dataclasses representing components, symbols, footprints, and search results
from LCSC and EasyEDA APIs.
"""

from dataclasses import dataclass, field


@dataclass
class Symbol:
    """Represents a schematic symbol."""

    uuid: str
    title: str
    description: str = ""
    prefix: str = ""  # e.g., "R", "C", "U"


@dataclass
class Footprint:
    """Represents a PCB footprint."""

    uuid: str
    title: str
    description: str = ""
    datasheet_url: str = ""


@dataclass
class Component:
    """Represents a component with symbols and footprints."""

    uuid: str
    title: str
    lcsc_id: str | None = None
    description: str = ""
    datasheet_url: str = ""
    manufacturer: str = ""
    category: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    symbols: list[Symbol] = field(default_factory=list)
    footprints: list[Footprint] = field(default_factory=list)

    @property
    def has_symbol(self) -> bool:
        return len(self.symbols) > 0

    @property
    def has_footprint(self) -> bool:
        return len(self.footprints) > 0


@dataclass
class SearchResult:
    """Represents paginated search results."""

    total: int
    page: int
    items_per_page: int
    results: list[Component] = field(default_factory=list)

    @property
    def total_pages(self) -> int:
        if self.items_per_page == 0:
            return 0
        return (self.total + self.items_per_page - 1) // self.items_per_page

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
