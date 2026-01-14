"""
Visual Width Calculation Module

Provides utilities for calculating visual width of text, especially for subtitle display.
"""

import math
import unicodedata
from functools import lru_cache


class VisualWidth:
    """
    Visual width calculation class providing static methods for text visual width calculation.

    This class provides utilities for calculating the visual width of text characters,
    especially designed for subtitle display. All methods are static.
    """

    # Character width constants

    # Very narrow characters (0.4 width)
    VERY_NARROW_CHARS: set[str] = {"i", "l", "I", "!", "|", "'", "`", ".", ",", ":", ";"}  # Note: uppercase I is very narrow

    # Narrow characters (0.6 width)
    NARROW_CHARS: set[str] = {"f", "j", "t", "r", "(", ")", "[", "]", "{", "}", '"', "/", "\\", "-"}

    # Wide characters (1.3 width)
    WIDE_CHARS: set[str] = {"m", "w", "M", "W", "@", "#", "%", "&", "*", "+", "="}

    @staticmethod
    def _get_char_width(char: str) -> float:
        """
        Get the visual width of a single character.

        Args:
            char: Single character string.

        Returns:
            float: Visual width (1.0 = standard Latin lowercase letter width).
        """
        if not char:
            return 0.0

        # ASCII fast path
        if ord(char) < 128:
            # Very narrow characters
            if char in VisualWidth.VERY_NARROW_CHARS:
                return 0.4

            # Narrow characters
            if char in VisualWidth.NARROW_CHARS:
                return 0.6

            # Wide characters
            if char in VisualWidth.WIDE_CHARS:
                return 1.3

            # Digits (monospace)
            if char.isdigit():
                return 0.9

            # Space
            if char == " ":
                return 0.3

            # Tab character
            if char == "\t":
                return 2.0

            # Uppercase letters (except I, M, W)
            if char.isupper() and char not in ("I", "M", "W"):
                return 1.15

            # Default (standard lowercase letters and other ASCII)
            return 1.0

        # Unicode character processing
        # Get East Asian width property
        ea_width = unicodedata.east_asian_width(char)

        # Full-width and wide characters
        if ea_width in ("F", "W"):
            return 2.0

        # Half-width characters
        if ea_width == "H":
            return 1.0

        # Get character category
        category = unicodedata.category(char)

        # Zero-width characters
        if category in ("Mn", "Mc", "Me", "Cc", "Cf"):
            return 0.0

        # Check specific Unicode ranges
        code = ord(char)

        # CJK Unified Ideographs (main block)
        if 0x4E00 <= code <= 0x9FFF:
            return 2.0

        # CJK Extension blocks
        if (
            0x3400 <= code <= 0x4DBF  # Extension A
            or 0x20000 <= code <= 0x2A6DF  # Extension B
            or 0x2A700 <= code <= 0x2B73F  # Extension C
            or 0x2B740 <= code <= 0x2B81F  # Extension D
            or 0x2B820 <= code <= 0x2CEAF  # Extension E
            or 0x2CEB0 <= code <= 0x2EBEF  # Extension F
            or 0x2EBF0 <= code <= 0x2EE5F  # Extension I
            or 0x30000 <= code <= 0x3134F  # Extension G
            or 0x31350 <= code <= 0x323AF  # Extension H
        ):
            return 2.0

        # CJK Compatibility Ideographs
        if 0xF900 <= code <= 0xFAFF or 0x2F800 <= code <= 0x2FA1F:  # CJK Compatibility Ideographs  # CJK Compatibility Ideographs Supplement
            return 2.0

        # Bopomofo (Zhuyin)
        if 0x3100 <= code <= 0x312F:
            return 2.0

        # Japanese kana
        if 0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF:  # Hiragana  # Katakana
            return 2.0

        # Korean
        if (
            0xAC00 <= code <= 0xD7AF  # Hangul syllables
            or 0x1100 <= code <= 0x11FF  # Hangul jamo
            or 0x3130 <= code <= 0x318F  # Hangul compatibility jamo
            or 0xA960 <= code <= 0xA97F  # Hangul jamo extended-A
            or 0xD7B0 <= code <= 0xD7FF  # Hangul jamo extended-B
        ):
            return 2.0

        # CJK symbols and punctuation (treat all non-Latin punctuation as wide)
        if (
            0x3000 <= code <= 0x303F  # CJK symbols and punctuation
            or 0xFF00 <= code <= 0xFFEF  # Halfwidth and fullwidth forms
            or 0xFE30 <= code <= 0xFE4F  # CJK compatibility forms
            or 0xFE50 <= code <= 0xFE6F  # Small form variants
        ):
            return 2.0

        # Ideographic description characters
        if 0x2FF0 <= code <= 0x2FFF:
            return 2.0

        # Emoji (Basic Multilingual Plane and Supplementary Plane)
        if (
            0x1F300 <= code <= 0x1F6FF  # Miscellaneous symbols and pictographs
            or 0x1F900 <= code <= 0x1F9FF  # Supplemental symbols and pictographs
            or 0x1F600 <= code <= 0x1F64F  # Emoticons
            or 0x1F680 <= code <= 0x1F6FF  # Transport and map symbols
            or 0x2600 <= code <= 0x26FF  # Miscellaneous symbols
            or 0x2700 <= code <= 0x27BF  # Dingbats
        ):
            return 2.0

        # Handle ambiguous width characters
        if ea_width == "A":
            # Greek letters
            if 0x0370 <= code <= 0x03FF:
                if category == "Lu":  # Uppercase
                    return 1.1
                return 1.0

            # Cyrillic letters
            if 0x0400 <= code <= 0x04FF:
                if category == "Lu":  # Uppercase
                    return 1.15
                return 1.0

            # Latin extended
            if 0x0100 <= code <= 0x017F:
                if category == "Lu":  # Uppercase
                    return 1.1
                return 1.0

            # Default ambiguous characters
            return 1.0

        # Arabic letters
        if 0x0600 <= code <= 0x06FF:
            return 0.8

        # Hebrew letters
        if 0x0590 <= code <= 0x05FF:
            return 0.9

        # Thai
        if 0x0E00 <= code <= 0x0E7F:
            return 0.9

        # Devanagari (Sanskrit, Hindi, etc.)
        if 0x0900 <= code <= 0x097F:
            return 0.9

        # Other cases based on character category
        if category == "Lu":  # Other uppercase letters
            return 1.1
        elif category == "Nd":  # Other digits
            return 0.9

        # Default width
        return 1.0

    @staticmethod
    @lru_cache(maxsize=10000)
    def calc(text: str) -> float:
        """
        Calculate the visual width of text (for subtitle display).

        This method calculates the visual width of text (in character units),
        where 1.0 represents the width of a standard Latin lowercase letter.

        Character width mapping:
        - CJK characters (Chinese, Japanese, Korean): 2.0
        - Latin lowercase letters: ~1.0 (varies by character)
        - Latin uppercase letters: ~1.15 (except I=0.4, M/W=1.3)
        - Digits: 0.9
        - Space: 0.3
        - Very narrow characters (i, l, I, etc.): 0.4
        - Narrow characters (f, j, t, r, etc.): 0.6
        - Wide characters (m, w, M, W, etc.): 1.3

        Return value handling:
        - Return value is rounded up to one decimal place (always rounds up)
        - Examples: 1.23 → 1.3, 1.21 → 1.3, 1.20 → 1.2

        Args:
            text: Input text string.

        Returns:
            float: Visual width in character units, rounded up to one decimal place.
        """
        # Empty string returns 0.0
        if not text:
            return 0.0

        # Accumulate visual width of each character
        total_width = 0.0
        for char in text:
            # Get width of single character and accumulate
            total_width += VisualWidth._get_char_width(char)

        # Round up to one decimal place (always rounds up)
        # Implementation: multiply by 10, round up, then divide by 10
        # Example: 1.23 * 10 = 12.3 → ceil(12.3) = 13 → 13 / 10 = 1.3
        return math.ceil(total_width * 10) / 10
