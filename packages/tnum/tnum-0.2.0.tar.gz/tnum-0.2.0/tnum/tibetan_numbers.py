"""
Core Tibetan number conversion functions.
"""

# Unicode code points for Tibetan digits (U+0F20 to U+0F29)
TIBETAN_DIGITS = {
    0: "\u0F20",  # ༠
    1: "\u0F21",  # ༡
    2: "\u0F22",  # ༢
    3: "\u0F23",  # ༣
    4: "\u0F24",  # ༤
    5: "\u0F25",  # ༥
    6: "\u0F26",  # ༦
    7: "\u0F27",  # ༧
    8: "\u0F28",  # ༨
    9: "\u0F29",  # ༩
}

# Mapping from English digits to Tibetan digits
ENGLISH_TO_TIBETAN = {str(i): TIBETAN_DIGITS[i] for i in range(10)}

# Mapping from Tibetan digits to English digits
TIBETAN_TO_ENGLISH = {v: str(k) for k, v in TIBETAN_DIGITS.items()}


def to_tibetan(number):
    """
    Convert an English number to Tibetan numerals.
    
    Args:
        number: An integer, string of digits, or number with Tibetan digits
        
    Returns:
        str: The number represented in Tibetan numerals
        
    Examples:
        >>> to_tibetan(123)
        '༡༢༣'
        >>> to_tibetan("456")
        '༤༥༦'
        >>> to_tibetan(0)
        '༠'
    """
    if isinstance(number, int):
        number_str = str(number)
    elif isinstance(number, str):
        # Check if it's already Tibetan
        if is_tibetan_number(number):
            return number
        # Remove any non-digit characters except negative sign
        number_str = number.strip()
    else:
        raise TypeError(f"Expected int or str, got {type(number).__name__}")
    
    # Handle negative numbers
    is_negative = number_str.startswith("-")
    if is_negative:
        number_str = number_str[1:]
    
    # Convert each digit
    result = []
    for char in number_str:
        if char in ENGLISH_TO_TIBETAN:
            result.append(ENGLISH_TO_TIBETAN[char])
        elif char.isspace():
            continue  # Skip whitespace
        else:
            raise ValueError(f"Invalid digit character: {char}")
    
    tibetan_str = "".join(result)
    return f"-{tibetan_str}" if is_negative else tibetan_str


def from_tibetan(tibetan_str):
    """
    Convert Tibetan numerals to an English number string.
    
    Args:
        tibetan_str: A string containing Tibetan numerals
        
    Returns:
        str: The number as a string of English digits
        
    Examples:
        >>> from_tibetan("༡༢༣")
        '123'
        >>> from_tibetan("༤༥༦")
        '456'
        >>> from_tibetan("༠")
        '0'
    """
    if not isinstance(tibetan_str, str):
        raise TypeError(f"Expected str, got {type(tibetan_str).__name__}")
    
    # Handle negative numbers
    is_negative = tibetan_str.startswith("-")
    if is_negative:
        tibetan_str = tibetan_str[1:]
    
    # Convert each Tibetan digit
    result = []
    for char in tibetan_str:
        if char in TIBETAN_TO_ENGLISH:
            result.append(TIBETAN_TO_ENGLISH[char])
        elif char.isspace():
            continue  # Skip whitespace
        else:
            raise ValueError(f"Invalid Tibetan digit: {char}")
    
    if not result:
        raise ValueError("No valid Tibetan digits found")
    
    english_str = "".join(result)
    return f"-{english_str}" if is_negative else english_str


def is_tibetan_digit(char):
    """
    Check if a character is a Tibetan digit.
    
    Args:
        char: A single character
        
    Returns:
        bool: True if the character is a Tibetan digit, False otherwise
        
    Examples:
        >>> is_tibetan_digit("༡")
        True
        >>> is_tibetan_digit("1")
        False
    """
    return char in TIBETAN_TO_ENGLISH


def is_tibetan_number(text):
    """
    Check if a string contains only Tibetan digits (and optional negative sign).
    
    Args:
        text: A string to check
        
    Returns:
        bool: True if the string contains only Tibetan digits, False otherwise
        
    Examples:
        >>> is_tibetan_number("༡༢༣")
        True
        >>> is_tibetan_number("123")
        False
        >>> is_tibetan_number("-༡༢༣")
        True
    """
    if not isinstance(text, str):
        return False
    
    text = text.strip()
    if not text:
        return False
    
    # Check for negative sign
    if text.startswith("-"):
        text = text[1:]
    
    # All remaining characters must be Tibetan digits
    return all(is_tibetan_digit(char) or char.isspace() for char in text) and any(
        is_tibetan_digit(char) for char in text
    )


def to_tibetan_int(tibetan_str):
    """
    Convert Tibetan numerals to a Python integer.
    
    Args:
        tibetan_str: A string containing Tibetan numerals
        
    Returns:
        int: The number as a Python integer
        
    Examples:
        >>> to_tibetan_int("༡༢༣")
        123
        >>> to_tibetan_int("༤༥༦")
        456
    """
    return int(from_tibetan(tibetan_str))


def is_english_digit(char):
    """
    Check if a character is an English digit (0-9).
    
    Args:
        char: A single character
        
    Returns:
        bool: True if the character is an English digit, False otherwise
        
    Examples:
        >>> is_english_digit("1")
        True
        >>> is_english_digit("༡")
        False
        >>> is_english_digit("a")
        False
    """
    return char.isdigit() and char in ENGLISH_TO_TIBETAN


def is_english_number(text):
    """
    Check if a string contains only English digits (and optional negative sign).
    
    Args:
        text: A string to check
        
    Returns:
        bool: True if the string contains only English digits, False otherwise
        
    Examples:
        >>> is_english_number("123")
        True
        >>> is_english_number("༡༢༣")
        False
        >>> is_english_number("-123")
        True
        >>> is_english_number("12.34")
        False
    """
    if not isinstance(text, str):
        return False
    
    text = text.strip()
    if not text:
        return False
    
    # Check for negative sign
    if text.startswith("-"):
        text = text[1:]
    
    # All remaining characters must be English digits
    return all(char.isdigit() and char in ENGLISH_TO_TIBETAN or char.isspace() for char in text) and any(
        char.isdigit() and char in ENGLISH_TO_TIBETAN for char in text
    )


# Roman numeral mappings
ROMAN_NUMERALS = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]

ROMAN_TO_VALUE = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


def to_roman(number):
    """
    Convert an integer to Roman numerals.
    
    Args:
        number: An integer (must be between 1 and 3999)
        
    Returns:
        str: The number represented in Roman numerals
        
    Examples:
        >>> to_roman(1)
        'I'
        >>> to_roman(4)
        'IV'
        >>> to_roman(9)
        'IX'
        >>> to_roman(1994)
        'MCMXCIV'
    """
    if not isinstance(number, int):
        raise TypeError(f"Expected int, got {type(number).__name__}")
    
    if number < 1:
        raise ValueError("Roman numerals can only represent positive integers (1-3999)")
    if number > 3999:
        raise ValueError("Roman numerals can only represent numbers up to 3999")
    
    result = []
    for value, numeral in ROMAN_NUMERALS:
        count = number // value
        result.append(numeral * count)
        number -= value * count
    
    return "".join(result)


def from_roman(roman_str):
    """
    Convert Roman numerals to an integer.
    
    Args:
        roman_str: A string containing Roman numerals
        
    Returns:
        int: The number as a Python integer
        
    Examples:
        >>> from_roman("I")
        1
        >>> from_roman("IV")
        4
        >>> from_roman("IX")
        9
        >>> from_roman("MCMXCIV")
        1994
    """
    if not isinstance(roman_str, str):
        raise TypeError(f"Expected str, got {type(roman_str).__name__}")
    
    roman_str = roman_str.strip().upper()
    if not roman_str:
        raise ValueError("Empty Roman numeral string")
    
    # Validate characters
    for char in roman_str:
        if char not in ROMAN_TO_VALUE:
            raise ValueError(f"Invalid Roman numeral character: {char}")
    
    result = 0
    i = 0
    while i < len(roman_str):
        # Check for subtractive notation (e.g., IV, IX, XL, XC, CD, CM)
        # This happens when a smaller value precedes a larger value
        if i + 1 < len(roman_str):
            current_value = ROMAN_TO_VALUE[roman_str[i]]
            next_value = ROMAN_TO_VALUE[roman_str[i + 1]]
            
            if current_value < next_value:
                # Subtractive notation
                result += next_value - current_value
                i += 2
                continue
        
        # Single character or normal additive notation
        result += ROMAN_TO_VALUE[roman_str[i]]
        i += 1
    
    return result


def is_roman_numeral(text):
    """
    Check if a string is a valid Roman numeral.
    
    Args:
        text: A string to check
        
    Returns:
        bool: True if the string is a valid Roman numeral, False otherwise
        
    Examples:
        >>> is_roman_numeral("IV")
        True
        >>> is_roman_numeral("MCMXCIV")
        True
        >>> is_roman_numeral("123")
        False
        >>> is_roman_numeral("ABC")
        False
    """
    if not isinstance(text, str):
        return False
    
    text = text.strip().upper()
    if not text:
        return False
    
    # Check if all characters are valid Roman numeral characters
    if not all(char in ROMAN_TO_VALUE for char in text):
        return False
    
    # Try to convert and convert back to verify validity
    try:
        value = from_roman(text)
        converted_back = to_roman(value)
        return converted_back == text
    except (ValueError, TypeError):
        return False


def tibetan_to_roman(tibetan_str):
    """
    Convert Tibetan numerals to Roman numerals.
    
    Args:
        tibetan_str: A string containing Tibetan numerals
        
    Returns:
        str: The number represented in Roman numerals
        
    Examples:
        >>> tibetan_to_roman("༡")
        'I'
        >>> tibetan_to_roman("༤")
        'IV'
        >>> tibetan_to_roman("༡༩༩༤")
        'MCMXCIV'
    """
    # Convert Tibetan to integer, then to Roman
    value = to_tibetan_int(tibetan_str)
    if value < 1:
        raise ValueError("Roman numerals can only represent positive integers (1-3999)")
    return to_roman(value)


def roman_to_tibetan(roman_str):
    """
    Convert Roman numerals to Tibetan numerals.
    
    Args:
        roman_str: A string containing Roman numerals
        
    Returns:
        str: The number represented in Tibetan numerals
        
    Examples:
        >>> roman_to_tibetan("I")
        '༡'
        >>> roman_to_tibetan("IV")
        '༤'
        >>> roman_to_tibetan("MCMXCIV")
        '༡༩༩༤'
    """
    # Convert Roman to integer, then to Tibetan
    value = from_roman(roman_str)
    return to_tibetan(value)

