from typing import Final

# Unicode base code points
HANGUL_BASE: Final[int] = 0xAC00
HANGUL_END: Final[int] = 0xD7A3

JAMO_LEAD_BASE: Final[int] = 0x1100
JAMO_VOWEL_BASE: Final[int] = 0x1161
JAMO_TAIL_BASE: Final[int] = 0x11A8

HCJ_BASE: Final[int] = 0x3131
HCJ_END: Final[int] = 0x318E

# Note: HCJ characters are stored directly in lists for fast access
# Lists provide faster indexing than tuples in most cases!

# Syllable composition constants
NUM_LEAD: Final[int] = 19
NUM_VOWEL: Final[int] = 21
NUM_TAIL: Final[int] = 28  # Includes no-tail case (0)

# Derived constants for syllable calculation
NUM_SYLLABLES_PER_LEAD: Final[int] = NUM_VOWEL * NUM_TAIL  # 588
TOTAL_SYLLABLES: Final[int] = NUM_LEAD * NUM_SYLLABLES_PER_LEAD  # 11172

# Modern Jamo characters (U+11xx)
# Leading consonants (초성)
JAMO_LEADS: Final[list[str]] = [chr(i) for i in range(0x1100, 0x1113)]

# Vowels (중성)
JAMO_VOWELS: Final[list[str]] = [chr(i) for i in range(0x1161, 0x1176)]

# Trailing consonants (종성) - None for no trailing consonant
JAMO_TAILS: Final[list[str | None]] = [None] + [chr(i) for i in range(0x11A8, 0x11C3)]

# Hangul Compatibility Jamo (HCJ, U+31xx)
# These are the compatibility forms used in standalone jamo
HCJ_CONSONANTS: Final[list[str]] = [
    "ㄱ",
    "ㄲ",
    "ㄳ",
    "ㄴ",
    "ㄵ",
    "ㄶ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㄺ",
    "ㄻ",
    "ㄼ",
    "ㄽ",
    "ㄾ",
    "ㄿ",
    "ㅀ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅄ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]

HCJ_VOWELS: Final[list[str]] = [
    "ㅏ",
    "ㅐ",
    "ㅑ",
    "ㅒ",
    "ㅓ",
    "ㅔ",
    "ㅕ",
    "ㅖ",
    "ㅗ",
    "ㅘ",
    "ㅙ",
    "ㅚ",
    "ㅛ",
    "ㅜ",
    "ㅝ",
    "ㅞ",
    "ㅟ",
    "ㅠ",
    "ㅡ",
    "ㅢ",
    "ㅣ",
]

# Leading consonants in HCJ form
HCJ_LEADS: Final[list[str]] = [
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]

# Trailing consonants in HCJ form
HCJ_TAILS: Final[list[str | None]] = [
    None,
    "ㄱ",
    "ㄲ",
    "ㄳ",
    "ㄴ",
    "ㄵ",
    "ㄶ",
    "ㄷ",
    "ㄹ",
    "ㄺ",
    "ㄻ",
    "ㄼ",
    "ㄽ",
    "ㄾ",
    "ㄿ",
    "ㅀ",
    "ㅁ",
    "ㅂ",
    "ㅄ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]

# Fast lookup dictionaries using Python 3.13 optimizations
# These provide O(1) lookup for index-to-character and character-to-index
LEAD_TO_INDEX: Final[dict[str, int]] = {lead: i for i, lead in enumerate(HCJ_LEADS)}

VOWEL_TO_INDEX: Final[dict[str, int]] = {vowel: i for i, vowel in enumerate(HCJ_VOWELS)}

TAIL_TO_INDEX: Final[dict[str | None, int]] = {
    tail: i for i, tail in enumerate(HCJ_TAILS)
}

# Jamo to HCJ mapping
JAMO_TO_HCJ: Final[dict[str, str]] = (
    {jamo: hcj for jamo, hcj in zip(JAMO_LEADS, HCJ_LEADS, strict=True)}
    | {jamo: hcj for jamo, hcj in zip(JAMO_VOWELS, HCJ_VOWELS, strict=True)}
    | {jamo: hcj for jamo, hcj in zip(JAMO_TAILS[1:], HCJ_TAILS[1:], strict=True)}
)  # type: ignore

# HCJ to Jamo mapping
HCJ_TO_JAMO_LEAD: Final[dict[str, str]] = {
    hcj: jamo for jamo, hcj in zip(JAMO_LEADS, HCJ_LEADS, strict=True)
}

HCJ_TO_JAMO_VOWEL: Final[dict[str, str]] = {
    hcj: jamo for jamo, hcj in zip(JAMO_VOWELS, HCJ_VOWELS, strict=True)
}

HCJ_TO_JAMO_TAIL: Final[dict[str, str]] = {
    hcj: jamo for jamo, hcj in zip(JAMO_TAILS[1:], HCJ_TAILS[1:], strict=True)
}  # type: ignore

# Compound jamo components (double consonants, clusters, diphthongs)
JAMO_COMPOUNDS: Final[dict[str, tuple[str, ...]]] = {
    # Double consonants (쌍자음)
    "ㄲ": ("ㄱ", "ㄱ"),
    "ㄸ": ("ㄷ", "ㄷ"),
    "ㅃ": ("ㅂ", "ㅂ"),
    "ㅆ": ("ㅅ", "ㅅ"),
    "ㅉ": ("ㅈ", "ㅈ"),
    # Consonant clusters (자음군)
    "ㄳ": ("ㄱ", "ㅅ"),
    "ㄵ": ("ㄴ", "ㅈ"),
    "ㄶ": ("ㄴ", "ㅎ"),
    "ㄺ": ("ㄹ", "ㄱ"),
    "ㄻ": ("ㄹ", "ㅁ"),
    "ㄼ": ("ㄹ", "ㅂ"),
    "ㄽ": ("ㄹ", "ㅅ"),
    "ㄾ": ("ㄹ", "ㅌ"),
    "ㄿ": ("ㄹ", "ㅍ"),
    "ㅀ": ("ㄹ", "ㅎ"),
    "ㅄ": ("ㅂ", "ㅅ"),
    # Diphthongs (이중모음)
    "ㅘ": ("ㅗ", "ㅏ"),
    "ㅙ": ("ㅗ", "ㅐ"),
    "ㅚ": ("ㅗ", "ㅣ"),
    "ㅝ": ("ㅜ", "ㅓ"),
    "ㅞ": ("ㅜ", "ㅔ"),
    "ㅟ": ("ㅜ", "ㅣ"),
    "ㅢ": ("ㅡ", "ㅣ"),
}

# Reverse lookup for composing jamo
COMPONENTS_TO_JAMO: Final[dict[tuple[str, ...], str]] = {
    components: jamo for jamo, components in JAMO_COMPOUNDS.items()
}

# Frozen sets for fast membership testing
# Note: Most validation now uses range checks or dict membership for better performance
COMPOUND_JAMO_SET: Final[frozenset[str]] = frozenset(JAMO_COMPOUNDS.keys())
