"""phone-toolkit: International phone number parsing, validation, and formatting.

This library provides utilities for parsing, validating, and formatting
international phone numbers with support for 200+ countries.

Example:
    >>> from phone_parser import parse, set_default_country_code
    >>> phone = parse("+385915125486")
    >>> phone.format("europe")
    '+385 (0) 91 512 5486'
"""

from phone_parser.country import Country, CountryRegistry
from phone_parser.phone import (
    Phone,
    is_valid,
    parse,
    set_default_area_code,
    set_default_country_code,
)

__version__ = "0.1.0"
__all__ = [
    "Country",
    "CountryRegistry",
    "Phone",
    "is_valid",
    "parse",
    "set_default_area_code",
    "set_default_country_code",
]
