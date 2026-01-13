"""
Tests for the Tibetan numbers library.
"""

import pytest
from tnum import (
    to_tibetan,
    from_tibetan,
    to_tibetan_int,
    is_tibetan_digit,
    is_tibetan_number,
    is_english_digit,
    is_english_number,
    to_roman,
    from_roman,
    is_roman_numeral,
    TIBETAN_DIGITS,
    ENGLISH_TO_TIBETAN,
    TIBETAN_TO_ENGLISH,
)


class TestToTibetan:
    """Tests for to_tibetan function."""

    def test_single_digits(self):
        """Test conversion of single digits."""
        assert to_tibetan(0) == "༠"
        assert to_tibetan(1) == "༡"
        assert to_tibetan(2) == "༢"
        assert to_tibetan(3) == "༣"
        assert to_tibetan(4) == "༤"
        assert to_tibetan(5) == "༥"
        assert to_tibetan(6) == "༦"
        assert to_tibetan(7) == "༧"
        assert to_tibetan(8) == "༨"
        assert to_tibetan(9) == "༩"

    def test_multi_digit_numbers(self):
        """Test conversion of multi-digit numbers."""
        assert to_tibetan(10) == "༡༠"
        assert to_tibetan(123) == "༡༢༣"
        assert to_tibetan(456) == "༤༥༦"
        assert to_tibetan(789) == "༧༨༩"
        assert to_tibetan(2024) == "༢༠༢༤"

    def test_string_input(self):
        """Test conversion from string input."""
        assert to_tibetan("123") == "༡༢༣"
        assert to_tibetan("0") == "༠"
        assert to_tibetan("999") == "༩༩༩"

    def test_negative_numbers(self):
        """Test conversion of negative numbers."""
        assert to_tibetan(-1) == "-༡"
        assert to_tibetan(-123) == "-༡༢༣"
        assert to_tibetan("-42") == "-༤༢"

    def test_already_tibetan(self):
        """Test that Tibetan input is returned as-is."""
        assert to_tibetan("༡༢༣") == "༡༢༣"

    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(TypeError):
            to_tibetan(None)
        with pytest.raises(TypeError):
            to_tibetan([])
        with pytest.raises(ValueError):
            to_tibetan("abc")


class TestFromTibetan:
    """Tests for from_tibetan function."""

    def test_single_digits(self):
        """Test conversion of single Tibetan digits."""
        assert from_tibetan("༠") == "0"
        assert from_tibetan("༡") == "1"
        assert from_tibetan("༢") == "2"
        assert from_tibetan("༣") == "3"
        assert from_tibetan("༤") == "4"
        assert from_tibetan("༥") == "5"
        assert from_tibetan("༦") == "6"
        assert from_tibetan("༧") == "7"
        assert from_tibetan("༨") == "8"
        assert from_tibetan("༩") == "9"

    def test_multi_digit_numbers(self):
        """Test conversion of multi-digit Tibetan numbers."""
        assert from_tibetan("༡༠") == "10"
        assert from_tibetan("༡༢༣") == "123"
        assert from_tibetan("༤༥༦") == "456"
        assert from_tibetan("༢༠༢༤") == "2024"

    def test_negative_numbers(self):
        """Test conversion of negative Tibetan numbers."""
        assert from_tibetan("-༡") == "-1"
        assert from_tibetan("-༡༢༣") == "-123"
        assert from_tibetan("-༤༢") == "-42"

    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(TypeError):
            from_tibetan(None)
        with pytest.raises(TypeError):
            from_tibetan(123)
        with pytest.raises(ValueError):
            from_tibetan("abc")
        with pytest.raises(ValueError):
            from_tibetan("")


class TestToTibetanInt:
    """Tests for to_tibetan_int function."""

    def test_basic_conversion(self):
        """Test basic integer conversion."""
        assert to_tibetan_int("༡༢༣") == 123
        assert to_tibetan_int("༤༥༦") == 456
        assert to_tibetan_int("༠") == 0
        assert to_tibetan_int("༢༠༢༤") == 2024

    def test_negative_numbers(self):
        """Test conversion of negative numbers."""
        assert to_tibetan_int("-༡") == -1
        assert to_tibetan_int("-༡༢༣") == -123


class TestIsTibetanDigit:
    """Tests for is_tibetan_digit function."""

    def test_tibetan_digits(self):
        """Test that Tibetan digits are recognized."""
        for i in range(10):
            assert is_tibetan_digit(TIBETAN_DIGITS[i]) is True

    def test_english_digits(self):
        """Test that English digits are not recognized."""
        for i in range(10):
            assert is_tibetan_digit(str(i)) is False

    def test_other_characters(self):
        """Test that other characters are not recognized."""
        assert is_tibetan_digit("a") is False
        assert is_tibetan_digit(" ") is False
        assert is_tibetan_digit("中") is False


class TestIsTibetanNumber:
    """Tests for is_tibetan_number function."""

    def test_valid_tibetan_numbers(self):
        """Test that valid Tibetan numbers are recognized."""
        assert is_tibetan_number("༡༢༣") is True
        assert is_tibetan_number("༠") is True
        assert is_tibetan_number("༢༠༢༤") is True
        assert is_tibetan_number("-༡༢༣") is True

    def test_english_numbers(self):
        """Test that English numbers are not recognized."""
        assert is_tibetan_number("123") is False
        assert is_tibetan_number("0") is False

    def test_mixed_content(self):
        """Test that mixed content is not recognized."""
        assert is_tibetan_number("༡2༣") is False
        assert is_tibetan_number("abc") is False

    def test_empty_string(self):
        """Test that empty string is not recognized."""
        assert is_tibetan_number("") is False

    def test_invalid_types(self):
        """Test that non-string types return False."""
        assert is_tibetan_number(123) is False
        assert is_tibetan_number(None) is False


class TestRoundTrip:
    """Tests for round-trip conversions."""

    def test_round_trip_integers(self):
        """Test that converting to Tibetan and back preserves the number."""
        test_numbers = [0, 1, 10, 42, 100, 999, 2024, 12345]
        for num in test_numbers:
            tibetan = to_tibetan(num)
            back = to_tibetan_int(tibetan)
            assert back == num, f"Failed for {num}: {tibetan} -> {back}"

    def test_round_trip_strings(self):
        """Test that converting to Tibetan and back preserves the string."""
        test_numbers = ["0", "1", "10", "42", "100", "999", "2024"]
        for num_str in test_numbers:
            tibetan = to_tibetan(num_str)
            back = from_tibetan(tibetan)
            assert back == num_str, f"Failed for {num_str}: {tibetan} -> {back}"

    def test_round_trip_negative(self):
        """Test round-trip conversion of negative numbers."""
        test_numbers = [-1, -42, -123, -2024]
        for num in test_numbers:
            tibetan = to_tibetan(num)
            back = to_tibetan_int(tibetan)
            assert back == num, f"Failed for {num}: {tibetan} -> {back}"


class TestConstants:
    """Tests for module constants."""

    def test_tibetan_digits_completeness(self):
        """Test that TIBETAN_DIGITS contains all digits 0-9."""
        assert len(TIBETAN_DIGITS) == 10
        for i in range(10):
            assert i in TIBETAN_DIGITS

    def test_english_to_tibetan_mapping(self):
        """Test that ENGLISH_TO_TIBETAN mapping is correct."""
        for i in range(10):
            assert ENGLISH_TO_TIBETAN[str(i)] == TIBETAN_DIGITS[i]

    def test_tibetan_to_english_mapping(self):
        """Test that TIBETAN_TO_ENGLISH mapping is correct."""
        for i in range(10):
            assert TIBETAN_TO_ENGLISH[TIBETAN_DIGITS[i]] == str(i)


class TestIsEnglishDigit:
    """Tests for is_english_digit function."""

    def test_english_digits(self):
        """Test that English digits are recognized."""
        for i in range(10):
            assert is_english_digit(str(i)) is True

    def test_tibetan_digits(self):
        """Test that Tibetan digits are not recognized."""
        for i in range(10):
            assert is_english_digit(TIBETAN_DIGITS[i]) is False

    def test_other_characters(self):
        """Test that other characters are not recognized."""
        assert is_english_digit("a") is False
        assert is_english_digit(" ") is False


class TestIsEnglishNumber:
    """Tests for is_english_number function."""

    def test_valid_english_numbers(self):
        """Test that valid English numbers are recognized."""
        assert is_english_number("123") is True
        assert is_english_number("0") is True
        assert is_english_number("2024") is True
        assert is_english_number("-123") is True

    def test_tibetan_numbers(self):
        """Test that Tibetan numbers are not recognized."""
        assert is_english_number("༡༢༣") is False
        assert is_english_number("༠") is False

    def test_invalid_formats(self):
        """Test that invalid formats are not recognized."""
        assert is_english_number("12.34") is False
        assert is_english_number("abc") is False
        assert is_english_number("") is False

    def test_invalid_types(self):
        """Test that non-string types return False."""
        assert is_english_number(123) is False
        assert is_english_number(None) is False


class TestToRoman:
    """Tests for to_roman function."""

    def test_single_digits(self):
        """Test conversion of single digit numbers."""
        assert to_roman(1) == "I"
        assert to_roman(5) == "V"
        assert to_roman(10) == "X"
        assert to_roman(50) == "L"
        assert to_roman(100) == "C"
        assert to_roman(500) == "D"
        assert to_roman(1000) == "M"

    def test_subtractive_notation(self):
        """Test subtractive notation (IV, IX, etc.)."""
        assert to_roman(4) == "IV"
        assert to_roman(9) == "IX"
        assert to_roman(40) == "XL"
        assert to_roman(90) == "XC"
        assert to_roman(400) == "CD"
        assert to_roman(900) == "CM"

    def test_complex_numbers(self):
        """Test conversion of complex numbers."""
        assert to_roman(1994) == "MCMXCIV"
        assert to_roman(2024) == "MMXXIV"
        assert to_roman(3888) == "MMMDCCCLXXXVIII"

    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(TypeError):
            to_roman("123")
        with pytest.raises(ValueError):
            to_roman(0)
        with pytest.raises(ValueError):
            to_roman(-1)
        with pytest.raises(ValueError):
            to_roman(4000)


class TestFromRoman:
    """Tests for from_roman function."""

    def test_single_digits(self):
        """Test conversion of single Roman numerals."""
        assert from_roman("I") == 1
        assert from_roman("V") == 5
        assert from_roman("X") == 10
        assert from_roman("L") == 50
        assert from_roman("C") == 100
        assert from_roman("D") == 500
        assert from_roman("M") == 1000

    def test_subtractive_notation(self):
        """Test subtractive notation."""
        assert from_roman("IV") == 4
        assert from_roman("IX") == 9
        assert from_roman("XL") == 40
        assert from_roman("XC") == 90
        assert from_roman("CD") == 400
        assert from_roman("CM") == 900

    def test_complex_numbers(self):
        """Test conversion of complex Roman numerals."""
        assert from_roman("MCMXCIV") == 1994
        assert from_roman("MMXXIV") == 2024
        assert from_roman("MMMDCCCLXXXVIII") == 3888

    def test_case_insensitive(self):
        """Test that conversion is case insensitive."""
        assert from_roman("iv") == 4
        assert from_roman("MCMXCIV") == from_roman("mcmxciv")

    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(TypeError):
            from_roman(123)
        with pytest.raises(ValueError):
            from_roman("")
        with pytest.raises(ValueError):
            from_roman("ABC")


class TestIsRomanNumeral:
    """Tests for is_roman_numeral function."""

    def test_valid_roman_numerals(self):
        """Test that valid Roman numerals are recognized."""
        assert is_roman_numeral("IV") is True
        assert is_roman_numeral("IX") is True
        assert is_roman_numeral("MCMXCIV") is True
        assert is_roman_numeral("MMXXIV") is True

    def test_invalid_formats(self):
        """Test that invalid formats are not recognized."""
        assert is_roman_numeral("123") is False
        assert is_roman_numeral("ABC") is False
        assert is_roman_numeral("IIII") is False  # Should be IV
        assert is_roman_numeral("") is False

    def test_case_insensitive(self):
        """Test that detection is case insensitive."""
        assert is_roman_numeral("iv") is True
        assert is_roman_numeral("MCMXCIV") == is_roman_numeral("mcmxciv")

    def test_invalid_types(self):
        """Test that non-string types return False."""
        assert is_roman_numeral(123) is False
        assert is_roman_numeral(None) is False


class TestRomanRoundTrip:
    """Tests for round-trip Roman numeral conversions."""

    def test_round_trip(self):
        """Test that converting to Roman and back preserves the number."""
        test_numbers = [1, 4, 9, 10, 50, 100, 500, 1000, 1994, 2024, 3999]
        for num in test_numbers:
            roman = to_roman(num)
            back = from_roman(roman)
            assert back == num, f"Failed for {num}: {roman} -> {back}"

