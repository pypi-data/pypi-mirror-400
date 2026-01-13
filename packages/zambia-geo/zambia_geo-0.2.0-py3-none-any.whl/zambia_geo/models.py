from dataclasses import dataclass, field


@dataclass
class Province:
    """Represents a Zambian province."""

    name: str
    capital: str
    area_km2: float
    population: int
    constituencies: int


@dataclass
class City:
    """Represents a Zambian city or town."""

    name: str
    province: str
    is_capital: bool
    population: int = None
    constituencies: list[str] = field(default_factory=list)
