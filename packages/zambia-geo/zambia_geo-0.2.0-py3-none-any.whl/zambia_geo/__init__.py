"""
A Python package containing Zambian provinces and cities data.

This package provides easy access to geographical data about Zambia,
including all provinces and their major cities/towns.
"""

from .data import (
    get_all_provinces,
    get_province_cities,
    get_city_details,
    get_constituencies,
    search_cities,
    get_all_cities,
    validate_province,
    validate_city,
)

from .models import Province, City

__version__ = "0.2.0"
__all__ = [
    "get_all_provinces",
    "get_province_cities",
    "get_city_details",
    "get_constituencies",
    "search_cities",
    "get_all_cities",
    "validate_province",
    "validate_city",
    "Province",
    "City",
]
