from .constants import (
    COMPONENTS_TO_JAMO,
    COMPOUND_JAMO_SET,
    HANGUL_BASE,
    HCJ_LEADS,
    HCJ_TAILS,
    HCJ_TO_JAMO_LEAD,
    HCJ_TO_JAMO_TAIL,
    HCJ_TO_JAMO_VOWEL,
    HCJ_VOWELS,
    JAMO_COMPOUNDS,
    JAMO_LEAD_BASE,
    JAMO_TAIL_BASE,
    JAMO_TO_HCJ,
    JAMO_VOWEL_BASE,
    LEAD_TO_INDEX,
    NUM_SYLLABLES_PER_LEAD,
    NUM_TAIL,
    TAIL_TO_INDEX,
    VOWEL_TO_INDEX,
)


class HangeulError(Exception):
    """Base exception for Hangeul-related errors."""


class InvalidJamoError(HangeulError):
    """Raised when invalid jamo characters are encountered."""


class InvalidSyllableError(HangeulError):
    """Raised when invalid Hangul syllables are encountered."""


# Validation functions
def is_hangul_syllable(char: str) -> bool:
    """Check if a character is a Hangul syllable (U+AC00 to U+D7A3).

    Args:
        char: A single character to check

    Returns:
        True if the character is a Hangul syllable, False otherwise

    Examples:
        >>> is_hangul_syllable('한')
        True
        >>> is_hangul_syllable('a')
        False
        >>> is_hangul_syllable('ㄱ')
        False
    """
    return 0xAC00 <= ord(char) <= 0xD7A3


def is_jamo(char: str) -> bool:
    """Check if a character is a jamo character (U+11xx).

    Args:
        char: A single character to check

    Returns:
        True if the character is a jamo, False otherwise

    Examples:
        >>> is_jamo('ᄀ')
        True
        >>> is_jamo('ㄱ')
        False
        >>> is_jamo('한')
        False
    """
    code = ord(char)
    return (
        (0x1100 <= code <= 0x1112)
        or (0x1161 <= code <= 0x1175)
        or (0x11A8 <= code <= 0x11C2)
    )


def is_hcj(char: str) -> bool:
    """Check if a character is a Hangul Compatibility Jamo (U+31xx).

    Args:
        char: A single character to check

    Returns:
        True if the character is HCJ, False otherwise

    Examples:
        >>> is_hcj('ㄱ')
        True
        >>> is_hcj('ᄀ')
        False
        >>> is_hcj('한')
        False
    """
    code = ord(char)
    return (0x3131 <= code <= 0x318E) and code != 0x3164


def is_jamo_lead(char: str) -> bool:
    """Check if a character is a leading jamo consonant.

    Args:
        char: A single character to check

    Returns:
        True if the character is a leading jamo, False otherwise
    """
    return char in LEAD_TO_INDEX


def is_jamo_vowel(char: str) -> bool:
    """Check if a character is a jamo vowel.

    Args:
        char: A single character to check

    Returns:
        True if the character is a jamo vowel, False otherwise
    """
    return char in VOWEL_TO_INDEX


def is_jamo_tail(char: str) -> bool:
    """Check if a character is a trailing jamo consonant.

    Args:
        char: A single character to check

    Returns:
        True if the character is a trailing jamo, False otherwise
    """
    return char in TAIL_TO_INDEX and char is not None


def is_jamo_compound(char: str) -> bool:
    """Check if a jamo is a compound (double consonant, cluster, or diphthong).

    Args:
        char: A single character to check

    Returns:
        True if the character is a compound jamo, False otherwise

    Examples:
        >>> is_jamo_compound('ㄲ')
        True
        >>> is_jamo_compound('ㅘ')
        True
        >>> is_jamo_compound('ㄱ')
        False
    """
    return char in COMPOUND_JAMO_SET


# Lookup table for maximum performance
_DECOMPOSE_LOOKUP_TABLE: dict[str, str] | None = None


def _build_decompose_lookup_table() -> dict[str, str]:
    """Build a complete lookup table for all Hangul syllables.

    This table maps each Hangul syllable to its decomposed HCJ jamo string.
    Memory cost: ~1.7 MB for all 11,172 Hangul syllables.

    Returns:
        Dictionary mapping syllable characters to decomposed jamo strings
    """
    lookup = {}
    hangul_base = HANGUL_BASE
    num_per_lead = NUM_SYLLABLES_PER_LEAD
    num_tail = NUM_TAIL
    hcj_leads = HCJ_LEADS
    hcj_vowels = HCJ_VOWELS
    hcj_tails = HCJ_TAILS

    for code in range(0xAC00, 0xD7A4):  # All Hangul syllables
        index = code - hangul_base
        lead_index = index // num_per_lead
        vowel_index = (index % num_per_lead) // num_tail
        tail_index = index % num_tail

        # Build decomposed string
        if tail_index:
            decomposed = (
                hcj_leads[lead_index] + hcj_vowels[vowel_index] + hcj_tails[tail_index]
            )  # type: ignore
        else:
            decomposed = hcj_leads[lead_index] + hcj_vowels[vowel_index]

        lookup[chr(code)] = decomposed

    return lookup


def decompose_hcj(text: str) -> str:
    """Decompose Hangul syllables in text into HCJ jamo characters.

    Uses a pre-built lookup table for optimal performance (~2x faster than
    computation-based approach). The table is built lazily on first use and
    cached for subsequent calls. Memory cost: ~1.7 MB.

    For U+11xx jamo output, use decompose_jamo().

    Args:
        text: Input text containing Hangul syllables

    Returns:
        Text with Hangul syllables decomposed into HCJ jamo

    Examples:
        >>> decompose_hcj('한글')
        'ㅎㅏㄴㄱㅡㄹ'
        >>> decompose_hcj('Hello 한글!')
        'Hello ㅎㅏㄴㄱㅡㄹ!'
    """
    global _DECOMPOSE_LOOKUP_TABLE

    if _DECOMPOSE_LOOKUP_TABLE is None:
        _DECOMPOSE_LOOKUP_TABLE = _build_decompose_lookup_table()

    if not text:
        return ""

    result = []
    append = result.append
    lookup = _DECOMPOSE_LOOKUP_TABLE

    for char in text:
        if char in lookup:
            append(lookup[char])
        else:
            append(char)

    return "".join(result)


def decompose_jamo(text: str) -> str:
    """Decompose Hangul syllables in text into U+11xx jamo characters.

    This function outputs jamo in the U+1100-U+11FF Unicode range.
    For HCJ (Hangul Compatibility Jamo) output, use decompose().

    Args:
        text: Input text containing Hangul syllables

    Returns:
        Text with Hangul syllables decomposed into U+11xx jamo

    Examples:
        >>> decompose_jamo('한글')
        '한글'
        >>> decompose_jamo('Hello 한글!')
        'Hello 한글!'
    """
    if not text:
        return ""

    result = []
    append = result.append
    hangul_base = HANGUL_BASE
    num_per_lead = NUM_SYLLABLES_PER_LEAD
    num_tail = NUM_TAIL
    jamo_lead_base = JAMO_LEAD_BASE
    jamo_vowel_base = JAMO_VOWEL_BASE
    jamo_tail_base = JAMO_TAIL_BASE

    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            index = code - hangul_base
            lead_index = index // num_per_lead
            vowel_index = (index % num_per_lead) // num_tail
            tail_index = index % num_tail

            append(chr(jamo_lead_base + lead_index))
            append(chr(jamo_vowel_base + vowel_index))
            if tail_index:
                append(chr(jamo_tail_base + tail_index - 1))
        else:
            append(char)

    return "".join(result)


def compose_jamo(text: str) -> str:
    """Compose U+11xx jamo characters in text into Hangul syllables.

    This function takes U+1100-U+11FF jamo characters and composes them
    into Hangul syllables.

    Args:
        text: Input text containing U+11xx jamo characters

    Returns:
        Text with jamo characters composed into Hangul syllables

    Examples:
        >>> compose_jamo('한글')
        '한글'
        >>> compose_jamo('Hello 한글!')
        'Hello 한글!'
    """
    if not text:
        return ""

    result: list[str] = []
    i = 0
    length = len(text)
    hangul_base = HANGUL_BASE
    num_per_lead = NUM_SYLLABLES_PER_LEAD
    num_tail = NUM_TAIL
    jamo_lead_base = JAMO_LEAD_BASE
    jamo_vowel_base = JAMO_VOWEL_BASE
    jamo_tail_base = JAMO_TAIL_BASE

    while i < length:
        char = text[i]
        code = ord(char)

        # Check if this is a lead jamo (U+1100-U+1112)
        if 0x1100 <= code <= 0x1112:
            lead_index = code - jamo_lead_base

            # Check for vowel
            if i + 1 < length:
                vowel_code = ord(text[i + 1])
                if 0x1161 <= vowel_code <= 0x1175:
                    vowel_index = vowel_code - jamo_vowel_base

                    # Check for tail
                    tail_index = 0
                    consumed = 2
                    if i + 2 < length:
                        tail_code = ord(text[i + 2])
                        if 0x11A8 <= tail_code <= 0x11C2:
                            # Check lookahead: if next char is vowel, don't consume tail
                            if i + 3 < length:
                                next_code = ord(text[i + 3])
                                if 0x1161 <= next_code <= 0x1175:
                                    # Next is vowel, so tail should be lead of next syllable
                                    pass
                                else:
                                    tail_index = tail_code - jamo_tail_base + 1
                                    consumed = 3
                            else:
                                tail_index = tail_code - jamo_tail_base + 1
                                consumed = 3

                    # Compose syllable
                    syllable_index = (
                        lead_index * num_per_lead + vowel_index * num_tail + tail_index
                    )
                    result.append(chr(hangul_base + syllable_index))
                    i += consumed
                    continue

        # Not composable, add as-is
        result.append(char)
        i += 1

    return "".join(result)


def decompose_compound(jamo: str) -> tuple[str, ...]:
    """Decompose a compound jamo into its components.

    Args:
        jamo: A compound jamo character (e.g., 'ㄲ', 'ㅘ')

    Returns:
        A tuple of component jamo characters

    Raises:
        InvalidJamoError: If the input is not a compound jamo

    Examples:
        >>> decompose_compound('ㄲ')
        ('ㄱ', 'ㄱ')
        >>> decompose_compound('ㅘ')
        ('ㅗ', 'ㅏ')
    """
    if jamo not in JAMO_COMPOUNDS:
        raise InvalidJamoError(f"'{jamo}' is not a compound jamo")

    return JAMO_COMPOUNDS[jamo]


# Lookup tables for compose optimization
_COMPOSE_LOOKUP_2: dict[str, str] | None = None  # 2-jamo (lead+vowel)
_COMPOSE_LOOKUP_3: dict[str, str] | None = None  # 3-jamo (lead+vowel+tail)


def _build_compose_lookup_tables() -> tuple[dict[str, str], dict[str, str]]:
    """Build lookup tables for all possible jamo combinations.

    Creates two tables:
    1. 2-jamo combinations (초성+중성) -> 음절
    2. 3-jamo combinations (초성+중성+종성) -> 음절

    Memory cost: ~0.5 MB total for both tables.

    Returns:
        Tuple of (2-jamo table, 3-jamo table)
    """
    lookup_2 = {}
    lookup_3 = {}

    for lead in HCJ_LEADS:
        if lead is None:
            continue
        for vowel in HCJ_VOWELS:
            if vowel is None:
                continue

            lead_index = LEAD_TO_INDEX[lead]
            vowel_index = VOWEL_TO_INDEX[vowel]

            # 2-jamo: lead + vowel
            syllable_index = (
                lead_index * NUM_SYLLABLES_PER_LEAD + vowel_index * NUM_TAIL
            )
            lookup_2[lead + vowel] = chr(HANGUL_BASE + syllable_index)

            # 3-jamo: lead + vowel + tail
            for tail in HCJ_TAILS:
                if tail is None:
                    continue
                tail_index = TAIL_TO_INDEX[tail]
                syllable_index = (
                    lead_index * NUM_SYLLABLES_PER_LEAD
                    + vowel_index * NUM_TAIL
                    + tail_index
                )
                lookup_3[lead + vowel + tail] = chr(HANGUL_BASE + syllable_index)

    return lookup_2, lookup_3


def compose_hcj(text: str) -> str:
    """Compose HCJ jamo characters in text into Hangul syllables.

    Uses pre-built lookup tables for optimal performance. The tables are built
    lazily on first use and cached for subsequent calls. Memory cost: ~0.5 MB.

    Args:
        text: Input text containing HCJ jamo characters

    Returns:
        Text with jamo characters composed into Hangul syllables

    Examples:
        >>> compose_hcj('ㅎㅏㄴㄱㅡㄹ')
        '한글'
        >>> compose_hcj('Hello ㅎㅏㄴㄱㅡㄹ!')
        'Hello 한글!'
    """
    global _COMPOSE_LOOKUP_2, _COMPOSE_LOOKUP_3

    if _COMPOSE_LOOKUP_2 is None:
        _COMPOSE_LOOKUP_2, _COMPOSE_LOOKUP_3 = _build_compose_lookup_tables()

    if not text:
        return ""

    result: list[str] = []
    i = 0
    length = len(text)
    lookup_2 = _COMPOSE_LOOKUP_2
    lookup_3 = _COMPOSE_LOOKUP_3

    while i < length:
        # Try 3-jamo first (most common for composed syllables)
        if i + 2 < length:
            three_jamo = text[i : i + 3]
            if three_jamo in lookup_3:  # type: ignore
                # Check lookahead: if next char is vowel, use 2-jamo instead
                if i + 3 < length:
                    next_char = text[i + 3]
                    # If next char is vowel, the third jamo should be lead of next syllable
                    if next_char in VOWEL_TO_INDEX:
                        # Use 2-jamo composition instead
                        two_jamo = text[i : i + 2]
                        if two_jamo in lookup_2:
                            result.append(lookup_2[two_jamo])
                            i += 2
                            continue

                result.append(lookup_3[three_jamo])  # type: ignore
                i += 3
                continue

        # Try 2-jamo
        if i + 1 < length:
            two_jamo = text[i : i + 2]
            if two_jamo in lookup_2:
                result.append(lookup_2[two_jamo])
                i += 2
                continue

        # Not composable, add as-is
        result.append(text[i])
        i += 1

    return "".join(result)


def compose_compound(components: tuple[str, ...] | list[str]) -> str:
    """Compose component jamo into a compound jamo.

    Args:
        components: A tuple or list of component jamo characters

    Returns:
        The composed compound jamo

    Raises:
        InvalidJamoError: If the components cannot be composed

    Examples:
        >>> compose_compound(('ㄱ', 'ㄱ'))
        'ㄲ'
        >>> compose_compound(['ㅗ', 'ㅏ'])
        'ㅘ'
    """
    components_tuple = tuple(components)

    if components_tuple not in COMPONENTS_TO_JAMO:
        raise InvalidJamoError(f"Cannot compose compound jamo from: {components_tuple}")

    return COMPONENTS_TO_JAMO[components_tuple]


# Conversion functions
def jamo_to_hcj(char: str) -> str:
    """Convert a jamo character (U+11xx) to HCJ (U+31xx).

    Args:
        char: A jamo character

    Returns:
        The corresponding HCJ character, or the input if not convertible

    Examples:
        >>> jamo_to_hcj('ᄀ')
        'ㄱ'
    """
    return JAMO_TO_HCJ.get(char, char)


def hcj_to_jamo(char: str, position: str = "vowel") -> str:
    """Convert an HCJ character to jamo (U+11xx).

    Args:
        char: An HCJ character
        position: The position context ("lead", "vowel", "tail")

    Returns:
        The corresponding jamo character, or the input if not convertible

    Raises:
        InvalidJamoError: If the position is invalid

    Examples:
        >>> hcj_to_jamo('ㄱ', 'lead')
        'ᄀ'
        >>> hcj_to_jamo('ㅏ', 'vowel')
        'ᅡ'
    """
    match position:
        case "lead":
            return HCJ_TO_JAMO_LEAD.get(char, char)
        case "vowel":
            return HCJ_TO_JAMO_VOWEL.get(char, char)
        case "tail":
            return HCJ_TO_JAMO_TAIL.get(char, char)
        case _:
            raise InvalidJamoError(f"Invalid position: '{position}'")
