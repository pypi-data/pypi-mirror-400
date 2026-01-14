"""Hangeul - A modern Korean Hangul syllable and jamo manipulation library.

This library provides efficient functions for decomposing and composing Korean
Hangul syllables and jamo characters, optimized for Python 3.13+.

Examples:
    >>> import hangeul
    >>> hangeul.decompose_hcj('안녕하세요')
    'ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ'
    >>> hangeul.compose_hcj('ㅎㅏㄴㄱㅡㄹ')
    '한글'
    >>> hangeul.decompose_jamo('한글')
    '한글'
    >>> hangeul.compose_jamo('한글')
    '한글'
"""

from .constants import (
    HCJ_CONSONANTS,
    HCJ_LEADS,
    HCJ_TAILS,
    HCJ_VOWELS,
    JAMO_COMPOUNDS,
    JAMO_LEADS,
    JAMO_TAILS,
    JAMO_VOWELS,
)
from .core import (
    HangeulError,
    InvalidJamoError,
    InvalidSyllableError,
    compose_hcj,
    compose_jamo,
    compose_compound,
    decompose_hcj,
    decompose_jamo,
    decompose_compound,
    hcj_to_jamo,
    is_hangul_syllable,
    is_hcj,
    is_jamo,
    is_jamo_compound,
    is_jamo_lead,
    is_jamo_tail,
    is_jamo_vowel,
    jamo_to_hcj,
)

__version__ = '1.0.0'

__all__ = [
    # Version
    '__version__',
    # Main functions - HCJ
    'decompose_hcj',
    'compose_hcj',
    # Main functions - U+11xx Jamo
    'decompose_jamo',
    'compose_jamo',
    # Compound jamo
    'decompose_compound',
    'compose_compound',
    # Validation functions
    'is_hangul_syllable',
    'is_jamo',
    'is_hcj',
    'is_jamo_lead',
    'is_jamo_vowel',
    'is_jamo_tail',
    'is_jamo_compound',
    # Conversion functions
    'jamo_to_hcj',
    'hcj_to_jamo',
    # Exceptions
    'HangeulError',
    'InvalidJamoError',
    'InvalidSyllableError',
    # Constants
    'JAMO_LEADS',
    'JAMO_VOWELS',
    'JAMO_TAILS',
    'JAMO_COMPOUNDS',
    'HCJ_LEADS',
    'HCJ_VOWELS',
    'HCJ_TAILS',
    'HCJ_CONSONANTS',
]
