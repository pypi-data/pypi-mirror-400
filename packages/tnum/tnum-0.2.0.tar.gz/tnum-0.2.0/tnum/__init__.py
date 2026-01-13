"""
Tibetan Numbers Library (tnum)

A Python library for converting between English numerals, Tibetan numerals, and Roman numerals.
"""

from .tibetan_numbers import (
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
    tibetan_to_roman,
    roman_to_tibetan,
    TIBETAN_DIGITS,
    ENGLISH_TO_TIBETAN,
    TIBETAN_TO_ENGLISH,
    ROMAN_NUMERALS,
    ROMAN_TO_VALUE,
)

__version__ = "0.2.0"
__all__ = [
    "to_tibetan",
    "from_tibetan",
    "to_tibetan_int",
    "is_tibetan_digit",
    "is_tibetan_number",
    "is_english_digit",
    "is_english_number",
    "to_roman",
    "from_roman",
    "is_roman_numeral",
    "tibetan_to_roman",
    "roman_to_tibetan",
    "TIBETAN_DIGITS",
    "ENGLISH_TO_TIBETAN",
    "TIBETAN_TO_ENGLISH",
    "ROMAN_NUMERALS",
    "ROMAN_TO_VALUE",
]

