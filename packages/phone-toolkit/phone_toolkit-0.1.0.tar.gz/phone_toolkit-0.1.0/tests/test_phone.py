"""Tests for phone number parsing functionality."""

import pytest

from phone_parser import (
    CountryRegistry,
    Phone,
    is_valid,
    parse,
    set_default_area_code,
    set_default_country_code,
)


class TestPhoneParsing:
    """Test suite for phone number parsing."""

    def test_parse_with_country_code(self) -> None:
        """Test parsing phone number with explicit country code."""
        phone = parse("+385915125486")

        assert phone is not None
        assert phone.country_code == "+385"
        assert phone.area_code == "91"
        assert phone.number == "5125486"

    def test_parse_with_double_zero_prefix(self) -> None:
        """Test parsing with 00 prefix instead of +."""
        phone = parse("00385915125486")

        assert phone is not None
        assert phone.country_code == "+385"
        assert phone.area_code == "91"

    def test_parse_us_number(self) -> None:
        """Test parsing US phone number."""
        phone = parse("+12125551234")

        assert phone is not None
        assert phone.country_code == "+1"
        assert phone.area_code == "212"
        assert phone.number == "5551234"

    def test_parse_with_extension(self) -> None:
        """Test parsing phone number with extension."""
        phone = parse("+385915125486x148")

        assert phone is not None
        assert phone.extension != ""
        assert "148" in phone.extension

    def test_parse_relaxed_validation(self) -> None:
        """Test that parsing strips non-numeric characters."""
        phone = parse("blabla +385 91 512-5486 blabla")

        assert phone is not None
        assert phone.country_code == "+385"

    def test_parse_empty_string(self) -> None:
        """Test that empty string returns None."""
        phone = parse("")

        assert phone is None

    def test_parse_with_defaults(self) -> None:
        """Test parsing with default country and area codes."""
        set_default_country_code("385")
        set_default_area_code("47")

        phone = parse("451588")

        assert phone is not None
        assert phone.country_code == "+385"
        assert phone.area_code == "47"

        # Reset defaults
        set_default_country_code("")
        set_default_area_code("")

    def test_parse_missing_country_code_raises(self) -> None:
        """Test that missing country code raises ValueError."""
        set_default_country_code("")  # Clear default

        with pytest.raises(ValueError, match="country code"):
            parse("915125486")

    def test_parse_missing_area_code_raises(self) -> None:
        """Test that missing area code raises ValueError."""
        set_default_country_code("385")
        set_default_area_code("")  # Clear default

        with pytest.raises(ValueError, match="area code"):
            parse("5125486")

        # Reset
        set_default_country_code("")


class TestPhoneValidation:
    """Test suite for phone number validation."""

    def test_is_valid_with_valid_number(self) -> None:
        """Test is_valid returns True for valid number."""
        assert is_valid("+385915125486") is True

    def test_is_valid_with_invalid_number(self) -> None:
        """Test is_valid returns False for invalid number."""
        set_default_country_code("")
        set_default_area_code("")

        assert is_valid("invalid") is False
        assert is_valid("") is False


class TestPhoneFormatting:
    """Test suite for phone number formatting."""

    def test_format_default(self) -> None:
        """Test default formatting."""
        phone = Phone(number="5125486", area_code="91", country_code="+385")

        assert phone.format("default") == "+385915125486"

    def test_format_europe(self) -> None:
        """Test European formatting style."""
        phone = Phone(number="5125486", area_code="91", country_code="+385")

        formatted = phone.format("europe")
        assert "+385" in formatted
        assert "(0)" in formatted
        assert "91" in formatted

    def test_format_us(self) -> None:
        """Test US formatting style."""
        phone = Phone(number="5551234", area_code="212", country_code="+1")

        formatted = phone.format("us")
        assert formatted == "(212) 555-1234"

    def test_format_custom_pattern(self) -> None:
        """Test custom format pattern."""
        phone = Phone(number="5125486", area_code="91", country_code="+385")

        formatted = phone.format("%A/%f-%l")
        assert formatted == "091/512-5486"

    def test_format_with_extension(self) -> None:
        """Test formatting with extension."""
        phone = Phone(
            number="5125486", area_code="91", country_code="+385", extension="x143"
        )

        formatted = phone.format("default_with_extension")
        assert "+385915125486" in formatted
        assert "x143" in formatted

    def test_str_representation(self) -> None:
        """Test __str__ uses default format."""
        phone = Phone(number="5125486", area_code="91", country_code="+385")

        assert str(phone) == "+385915125486"

    def test_number_splitting(self) -> None:
        """Test number1 and number2 methods."""
        phone = Phone(
            number="5125486", area_code="91", country_code="+385", n1_length=3
        )

        assert phone.number1() == "512"
        assert phone.number2() == "5486"

    def test_area_code_long(self) -> None:
        """Test area_code_long adds leading zero."""
        phone = Phone(number="5125486", area_code="91", country_code="+385")

        assert phone.area_code_long() == "091"


class TestCountryLookup:
    """Test suite for country lookup functionality."""

    def test_find_country_by_code(self) -> None:
        """Test finding country by dialing code."""
        country = CountryRegistry.find_by_code("1")

        assert country is not None
        assert country.name == "United States"
        assert country.char_3_code == "US"

    def test_find_country_by_iso_code(self) -> None:
        """Test finding country by ISO code."""
        country = CountryRegistry.find_by_iso_code("US")

        assert country is not None
        assert country.country_code == "1"

    def test_find_country_by_iso_code_case_insensitive(self) -> None:
        """Test ISO code lookup is case-insensitive."""
        country_upper = CountryRegistry.find_by_iso_code("US")
        country_lower = CountryRegistry.find_by_iso_code("us")

        assert country_upper is not None
        assert country_lower is not None
        assert country_upper.country_code == country_lower.country_code

    def test_find_nonexistent_country(self) -> None:
        """Test that nonexistent country returns None."""
        country = CountryRegistry.find_by_code("999")

        assert country is None
