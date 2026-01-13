"""Core phone number parsing, validation, and formatting functionality."""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

from phone_parser.country import CountryRegistry

if TYPE_CHECKING:
    from re import Pattern

# Common regex patterns for parsing
COMMON_EXTENSIONS = r"(ext|ex|x|xt|#|:)+[^0-9]*([-0-9]{1,})*#?$"
COMMON_EXTRAS = r"(\(0\)|[^0-9+]|^\+?00?)"
FORMAT_TOKENS = r"(%[caAnflx])"

# Normalization replacements
EXTRA_REPLACEMENTS = {
    "(0)": "+",
    "00": "+",
    "+00": "+",
    "+0": "+",
}

# Named format patterns
NAMED_FORMATS = {
    "default": "+%c%a%n",
    "default_with_extension": "+%c%a%n%x",
    "europe": "+%c (0) %a %f %l",
    "us": "(%a) %f-%l",
}

# Thread-safe global defaults
_defaults_lock = threading.Lock()
_default_country_code: str | None = None
_default_area_code: str | None = None


def set_default_country_code(code: str) -> str:
    """Set global default country code for parsing incomplete numbers.

    Thread-safe setter for default country code used when parsing numbers
    without explicit country information.

    Args:
        code: Country dialing code (e.g., "1", "44", "86").

    Returns:
        The code that was set.

    Example:
        >>> set_default_country_code("1")
        '1'
    """
    global _default_country_code  # noqa: PLW0603
    with _defaults_lock:
        _default_country_code = code
    return code


def set_default_area_code(code: str) -> str:
    """Set global default area code for parsing incomplete numbers.

    Thread-safe setter for default area code used when parsing numbers
    without explicit area information.

    Args:
        code: Area/city code (e.g., "212", "20", "10").

    Returns:
        The code that was set.

    Example:
        >>> set_default_area_code("212")
        '212'
    """
    global _default_area_code  # noqa: PLW0603
    with _defaults_lock:
        _default_area_code = code
    return code


@dataclass
class Phone:
    """Represents a parsed phone number with all components.

    Attributes:
        number: Subscriber number (digits only).
        area_code: Area/city code.
        country_code: International dialing code (with + prefix).
        extension: Extension number if present.
        n1_length: Number of digits for first part of formatted number.
    """

    number: str
    area_code: str
    country_code: str
    extension: str = ""
    n1_length: int = 3

    def __str__(self) -> str:
        """Return default formatted representation.

        Returns:
            Phone number in "+{country}{area}{number}" format.
        """
        return self.format("default")

    def number1(self) -> str:
        """Get first N digits of number (for formatting).

        Returns:
            First n1_length digits of the subscriber number.

        Example:
            >>> phone = Phone(number="5125486", area_code="91", country_code="+385")
            >>> phone.number1()
            '512'
        """
        return self.number[: self.n1_length]

    def number2(self) -> str:
        """Get remaining digits of number (for formatting).

        Returns:
            Digits after the first n1_length characters.

        Example:
            >>> phone = Phone(number="5125486", area_code="91", country_code="+385")
            >>> phone.number2()
            '5486'
        """
        return self.number[self.n1_length :]

    def area_code_long(self) -> str:
        """Get area code with leading zero.

        Returns:
            Area code prefixed with "0", or empty string if no area code.

        Example:
            >>> phone = Phone(number="5125486", area_code="91", country_code="+385")
            >>> phone.area_code_long()
            '091'
        """
        return f"0{self.area_code}" if self.area_code else ""

    def format(self, fmt: str) -> str:
        """Format phone number using named format or custom pattern.

        Args:
            fmt: Format name ("default", "europe", "us") or custom pattern
                using tokens: %c (country), %a (area), %A (area with 0),
                %n (number), %f (first digits), %l (last digits), %x (ext).

        Returns:
            Formatted phone number string.

        Example:
            >>> phone = Phone(number="5125486", area_code="91", country_code="+385")
            >>> phone.format("%A/%f-%l")
            '091/512-5486'
            >>> phone.format("europe")
            '+385 (0) 91 512 5486'
        """
        # Use named format if it exists
        pattern = NAMED_FORMATS.get(fmt, fmt)
        return self._format_number(pattern)

    def _format_number(self, pattern: str) -> str:
        """Apply token replacements to format pattern.

        Args:
            pattern: Format string with %tokens.

        Returns:
            Formatted string with tokens replaced.
        """
        replacements = {
            "%c": self.country_code,
            "%a": self.area_code,
            "%A": self.area_code_long(),
            "%n": self.number,
            "%f": self.number1(),
            "%l": self.number2(),
            "%x": self.extension,
        }

        # Replace each token
        regex: Pattern[str] = re.compile(FORMAT_TOKENS)
        result = pattern
        for match in regex.findall(pattern):
            replacement = replacements.get(match, "")
            result = result.replace(match, replacement, 1)

        # Clean up double plus signs
        return _remove_useless_plus(result)


def parse(phone_string: str) -> Phone | None:
    """Parse phone number string into Phone object.

    Performs relaxed validation - strips non-numeric characters except '+'.
    Uses global defaults for country/area codes if not detected.

    Args:
        phone_string: Phone number string in any common format.

    Returns:
        Parsed Phone object, or None if input is empty.

    Raises:
        ValueError: If phone number is invalid or required components missing.

    Example:
        >>> phone = parse("+385915125486")
        >>> phone.country_code if phone else None
        '+385'
        >>> phone = parse("blabla 091/512-5486 blabla")  # Relaxed parsing
        >>> phone is not None
        True
    """
    if not phone_string.strip():
        return None

    # Extract extension first
    clean_number, extension = _extract_extension(phone_string)

    # Normalize to standard format
    clean_number = _normalize(clean_number)

    # Split into components
    number, area_code, country_code = _split_to_parts(clean_number)

    # Apply defaults if needed
    if not country_code:
        if _default_country_code:
            country_code = f"+{_default_country_code}"
        else:
            msg = "Must specify country code or set default"
            raise ValueError(msg)

    if not area_code:
        if _default_area_code:
            area_code = _default_area_code
        else:
            msg = "Must specify area code or set default"
            raise ValueError(msg)

    if not number:
        msg = "Must specify phone number"
        raise ValueError(msg)

    return Phone(
        number=number,
        area_code=area_code,
        country_code=country_code,
        extension=extension,
    )


def is_valid(phone_string: str) -> bool:
    """Check if phone number string is valid.

    Args:
        phone_string: Phone number string to validate.

    Returns:
        True if parseable, False otherwise.

    Example:
        >>> is_valid("+385915125486")
        True
        >>> is_valid("")
        False
    """
    try:
        return parse(phone_string) is not None
    except ValueError:
        return False


def _extract_extension(phone_string: str) -> tuple[str, str]:
    """Extract extension from phone number string.

    Args:
        phone_string: Full phone number string.

    Returns:
        Tuple of (number_without_extension, extension).
    """
    regex: Pattern[str] = re.compile(COMMON_EXTENSIONS)
    match = regex.search(phone_string)

    if match:
        extension = match.group()
        clean_number = regex.sub("", phone_string)
        return clean_number, extension

    return phone_string, ""


def _normalize(phone_string: str) -> str:
    """Normalize phone number by replacing common patterns.

    Args:
        phone_string: Raw phone number string.

    Returns:
        Normalized string with standardized prefixes.
    """
    result = phone_string
    regex: Pattern[str] = re.compile(COMMON_EXTRAS)

    # Replace common extras
    for match in regex.findall(result):
        replacement = EXTRA_REPLACEMENTS.get(match, "")
        result = regex.sub(replacement, result, count=1)

    return result


def _split_to_parts(phone_string: str) -> tuple[str, str, str]:
    """Split normalized phone number into components.

    Args:
        phone_string: Normalized phone number string.

    Returns:
        Tuple of (number, area_code, country_code).

    Raises:
        ValueError: If country code cannot be detected.
    """
    # Detect country from prefix
    country = CountryRegistry.detect_from_number(phone_string, _default_country_code)

    if country is None:
        msg = "Must specify country code"
        raise ValueError(msg)

    # Check if phone_string has country code prefix
    has_country_prefix = phone_string.startswith(f"+{country.country_code}")

    # Remove country code prefix and replace with leading zero
    country_regex = country.country_code_regexp()
    working_string = country_regex.sub("0", phone_string)

    # Detect format
    format_type = country.detect_format(working_string)
    if not format_type:
        msg = f"Invalid phone number format for country {country.name}"
        raise ValueError(msg)

    area_code = ""
    number = ""

    # Only extract area code from number if country prefix was present
    if has_country_prefix:
        # Extract area code (skip leading zero)
        area_regex = country.area_code_regexp()
        # Remove leading zero before matching area code
        working_no_zero = working_string.lstrip("0")
        area_match = area_regex.match(working_no_zero)
        area_code = area_match.group() if area_match else ""

        # Extract number (remove area code from working string without leading zeros)
        number = working_no_zero[len(area_code) :] if area_code else working_no_zero
    else:
        # No country prefix - treat entire string as the number
        # Area code will be filled from defaults in parse()
        number = working_string.lstrip("0")

    return number, area_code, f"+{country.country_code}"


def _remove_useless_plus(formatted: str) -> str:
    """Remove duplicate plus signs from formatted number.

    Args:
        formatted: Formatted phone number string.

    Returns:
        Cleaned string with single plus prefix.
    """
    regex: Pattern[str] = re.compile(r"^(\+ \+)|^(\+\+)")
    return regex.sub("+", formatted)
