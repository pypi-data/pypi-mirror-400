from typing import List, Tuple
from zambia_geo import (
    get_all_provinces,
    get_province_cities,
    get_all_cities,
)


def format_population(population: int) -> str:
    """Format population numbers for display."""
    if population is None:
        return "Unknown"
    if population >= 1_000_000:
        return f"{population / 1_000_000:.1f}M"
    if population >= 1_000:
        return f"{population / 1_000:.1f}K"
    return str(population)


def get_province_choices() -> List[Tuple[str, str]]:
    """Return province choices for Django models."""
    return [(province.name, province.name) for province in get_all_provinces()]


def get_city_choices(province_name: str = None) -> List[Tuple[str, str]]:
    """
    Return city choices for Django models.
    If province_name is None, returns all cities in Zambia.
    """
    if province_name:
        cities = get_province_cities(province_name)
    else:
        cities = get_all_cities()

    # Sort cities by name
    cities_sorted = sorted(cities, key=lambda x: x.name)
    return [(city.name, city.name) for city in cities_sorted]
