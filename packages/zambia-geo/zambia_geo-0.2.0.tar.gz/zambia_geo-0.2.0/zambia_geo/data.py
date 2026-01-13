from typing import List, Optional
from .models import Province, City
from .zambia_constituencies import ZAMBIA_CONSTITUENCIES as ZC

# Data source: Based on Zambia's 10 provinces and major cities/towns
PROVINCES_DATA = {
    "Central": {
        "capital": "Kabwe",
        "area_km2": 110450,
        "population": 1859000,
        "cities": [
            {"name": "Kabwe", "is_capital": True, "population": 202360},
            {"name": "Kapiri Mposhi", "is_capital": False,
                "population": 76000},
            {"name": "Mkushi", "is_capital": False, "population": 25000},
            {"name": "Serenje", "is_capital": False, "population": 23000},
        ],
    },
    "Copperbelt": {
        "capital": "Ndola",
        "area_km2": 31328,
        "population": 2583800,
        "cities": [
            {"name": "Ndola", "is_capital": True, "population": 451246},
            {"name": "Kitwe", "is_capital": False, "population": 517543},
            {"name": "Chingola", "is_capital": False, "population": 216626},
            {"name": "Luanshya", "is_capital": False, "population": 130076},
            {"name": "Mufulira", "is_capital": False, "population": 151309},
            {"name": "Chililabombwe", "is_capital": False,
                "population": 87920},
        ],
    },
    "Eastern": {
        "capital": "Chipata",
        "area_km2": 69106,
        "population": 1949000,
        "cities": [
            {"name": "Chipata", "is_capital": True, "population": 455783},
            {"name": "Lundazi", "is_capital": False, "population": 12000},
            {"name": "Petauke", "is_capital": False, "population": 19000},
        ],
    },
    "Luapula": {
        "capital": "Mansa",
        "area_km2": 50567,
        "population": 1200000,
        "cities": [
            {"name": "Mansa", "is_capital": True, "population": 129185},
            {"name": "Kawambwa", "is_capital": False, "population": 20000},
            {"name": "Nchelenge", "is_capital": False, "population": 15000},
        ],
    },
    "Lusaka": {
        "capital": "Lusaka",
        "area_km2": 21896,
        "population": 3100000,
        "cities": [
            {"name": "Lusaka", "is_capital": True, "population": 2467563},
            {"name": "Kafue", "is_capital": False, "population": 219000},
            {"name": "Luangwa", "is_capital": False, "population": 5000},
        ],
    },
    "Muchinga": {
        "capital": "Chinsali",
        "area_km2": 87606,
        "population": 895000,
        "cities": [
            {"name": "Chinsali", "is_capital": True, "population": 10000},
            {"name": "Nakonde", "is_capital": False, "population": 15000},
            {"name": "Isoka", "is_capital": False, "population": 12000},
        ],
    },
    "North-Western": {
        "capital": "Solwezi",
        "area_km2": 125827,
        "population": 830800,
        "cities": [
            {"name": "Solwezi", "is_capital": True, "population": 90000},
            {"name": "Mwinilunga", "is_capital": False, "population": 15000},
            {"name": "Zambezi", "is_capital": False, "population": 10000},
        ],
    },
    "Northern": {
        "capital": "Kasama",
        "area_km2": 147826,
        "population": 1300000,
        "cities": [
            {"name": "Kasama", "is_capital": True, "population": 101845},
            {"name": "Mbala", "is_capital": False, "population": 20000},
            {"name": "Mpika", "is_capital": False, "population": 25000},
        ],
    },
    "Southern": {
        "capital": "Choma",
        "area_km2": 85383,
        "population": 1864000,
        "cities": [
            {"name": "Choma", "is_capital": True, "population": 51000},
            {"name": "Livingstone", "is_capital": False, "population": 136897},
            {"name": "Mazabuka", "is_capital": False, "population": 71000},
            {"name": "Monze", "is_capital": False, "population": 30000},
        ],
    },
    "Western": {
        "capital": "Mongu",
        "area_km2": 126386,
        "population": 991500,
        "cities": [
            {"name": "Mongu", "is_capital": True, "population": 179585},
            {"name": "Sesheke", "is_capital": False, "population": 20000},
            {"name": "Kalabo", "is_capital": False, "population": 15000},
        ],
    },
}


def get_all_provinces() -> List[Province]:
    """Return a list of all provinces in Zambia."""
    return [
        Province(
            name=name,
            capital=data["capital"],
            area_km2=data["area_km2"],
            population=data["population"],
            constituencies=len(ZC[name]),
        )
        for name, data in PROVINCES_DATA.items()
    ]


def get_province_cities(province_name: str) -> List[City]:
    """Return a list of cities in the specified province."""
    province = PROVINCES_DATA.get(province_name.title())
    if not province:
        return []

    return [
        City(
            name=city["name"],
            province=province_name,
            is_capital=city["is_capital"],
            population=city.get("population"),
        )
        for city in province.get("cities", [])
    ]

def get_constituencies(province_name: str) -> List:
    province = ZC.get(province_name.title())
    if not province:
        return []

    return province


def get_city_details(city_name: str) -> Optional[City]:
    """Get details about a specific city."""
    for province_name, data in PROVINCES_DATA.items():
        for city in data.get("cities", []):
            if city["name"].lower() == city_name.lower():
                return City(
                    name=city["name"],
                    province=province_name,
                    is_capital=city["is_capital"],
                    population=city.get("population"),
                    constituencies=(ZC[city_name]),
                )
    return None


def search_cities(search_term: str) -> List[City]:
    """Search for cities by name."""
    results = []
    for province_name, data in PROVINCES_DATA.items():
        for city in data.get("cities", []):
            if search_term.lower() in city["name"].lower():
                results.append(
                    City(
                        name=city["name"],
                        province=province_name,
                        is_capital=city["is_capital"],
                        population=city.get("population"),
                    )
                )
    return results


def get_all_cities() -> List[City]:
    """Get all cities in Zambia."""
    cities = []
    for province_name, data in PROVINCES_DATA.items():
        cities.extend(
            [
                City(
                    name=city["name"],
                    province=province_name,
                    is_capital=city["is_capital"],
                    population=city.get("population"),
                )
                for city in data.get("cities", [])
            ]
        )
    return cities


def validate_province(province_name: str) -> bool:
    """Check if a province exists in Zambia."""
    return province_name.title() in PROVINCES_DATA


def validate_city(city_name: str) -> bool:
    """Check if a city exists in Zambia."""
    return any(
        city["name"].lower() == city_name.lower()
        for data in PROVINCES_DATA.values()
        for city in data.get("cities", [])
    )
