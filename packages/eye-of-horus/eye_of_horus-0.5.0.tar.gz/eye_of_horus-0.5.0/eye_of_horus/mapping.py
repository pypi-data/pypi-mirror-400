"""
Leiden transliteration → 16-position wheel mapping.

The wheel has 16 positions, each a fundamental phonemic verb.
This module handles transliteration conversion; see engine.py for
the complete hourglass semantics (5 positions per phoneme).

Wheel Lexicon v63 (January 2026):
| Pos | Ph  | Deity    | F eq      | M eq      |
|-----|-----|----------|-----------|-----------|
|  1  | n   | Neith    | WEAVE     | INTEGRATE |
|  2  | w   | Wadjet   | FLOW      | RADIATE   |
|  3  | s   | Sekhmet  | COCOON    | EMERGE    |
|  4  | sh  | Shu      | ALIGN     | DIRECT    |
|  5  | A   | Atum     | TEND      | LEAD      |
|  6  | t   | Seshat   | ETCH      | READ      |
|  7  | H   | Horus    | INTERPRET | EXPRESS   |
|  8  | r   | Ra       | BASK      | SHINE     |
|  9  | m   | Ma'at    | TRUST     | TRUE      |
| 10  | a   | Anubis   | ALLOW     | HONOUR    |
| 11  | y   | Isis     | RESTORE   | DEVOTE    |
| 12  | b   | Bes      | CULTIVATE | RECEIVE   |
| 13  | p   | Ptah     | GATHER    | STORE     |
| 14  | i   | Ihy      | PROTECT   | BESTOW    |
| 15  | kh  | Khnum    | CAPACITY  | EMBODY    |
| 16  | dj  | Thoth    | ACT       | DISCERN   |

Spine phonemes (NOT on wheel): x, d, k, q, g, f, h
"""

import re
from typing import List

# The 16 wheel phonemes in order
WHEEL_16 = ['n', 'w', 's', 'sh', 'A', 't', 'H', 'r', 'm', 'a', 'y', 'b', 'p', 'i', 'kh', 'dj']

# Phoneme to wheel position (0-indexed)
WHEEL_INDEX = {p: i for i, p in enumerate(WHEEL_16)}

# Core verbs for wheel phonemes (M equilibrium from v62 lexicon)
WHEEL_VERBS = {
    'n':  'INTEGRATE',  # Neith - weaving into coherence
    'w':  'RADIATE',   # Wadjet - life force, chi
    's':  'EMERGE',     # Sekhmet - transformation
    'sh': 'DIRECT',     # Shu - navigation
    'A':  'LEAD',       # Atum - shepherding
    't':  'READ',       # Seshat - inscription
    'H':  'EXPRESS',    # Horus - meaning
    'r':  'SHINE',      # Ra - radiance
    'm':  'TRUE',       # Ma'at - truth
    'a':  'HONOUR',     # Anubis - threshold
    'y':  'DEVOTE',     # Isis - devotion
    'b':  'RECEIVE',   # Taweret - cultivation
    'p':  'STORE',      # Ptah - gathering
    'i':  'BESTOW',     # Ihy - legacy
    'kh': 'EMBODY',     # Khnum - incarnation
    'dj': 'DISCERN',    # Thoth - discernment
}

# Spine phonemes (not on wheel) - for reference
SPINE_VERBS = {
    'x':  'FUNDAMENT',  # Cosmogenic axis
    'd':  'DO',         # Phylogenic axis
    'k':  'CYCLE',      # Ontogenic axis
    'g':  'GROUND',     # Secondary spine
    'f':  'BREATHE',    # Secondary spine
    'h':  'SEE',        # Secondary spine (glottal, not pharyngeal H)
}

# Leiden Unified Transliteration → Wheel mapping
# Includes all known Unicode variants for each phoneme
LEIDEN_TO_WHEEL = {
    # Position 1: n
    'n': 'n',
    
    # Position 2: w
    'w': 'w',
    'u': 'w',
    
    # Position 3: s
    's': 's',
    'z': 's',
    'ś': 's',      # s with acute (variant)
    
    # Position 4: sh
    'š': 'sh',
    
    # Position 5: A (aleph) — all Unicode variants
    'ꜣ': 'A',      # U+A723 EGYPTOLOGICAL ALEF (primary)
    'Ꜣ': 'A',      # U+A722 CAPITAL
    'ʾ': 'A',      # U+02BE MODIFIER RIGHT HALF RING
    'ʼ': 'A',      # U+02BC MODIFIER APOSTROPHE
    'ˀ': 'A',      # U+02C0 MODIFIER GLOTTAL STOP
    
    # Position 6: t
    't': 't',
    'ṯ': 't',      # U+1E6F t with line below
    'ṭ': 't',      # U+1E6D t with dot below
    
    # Position 7: H (pharyngeal) — DISTINCT from glottal h
    'ḥ': 'H',      # U+1E25 h with dot below
    
    # Position 8: r
    'r': 'r',
    'l': 'r',      # l → r (late Egyptian)
    
    # Position 9: m
    'm': 'm',
    
    # Position 10: a (ayin) — all Unicode variants
    'ꜥ': 'a',      # U+A725 EGYPTOLOGICAL AIN (primary)
    'Ꜥ': 'a',      # U+A724 CAPITAL
    'ʿ': 'a',      # U+02BF MODIFIER LEFT HALF RING
    
    # Position 11: y
    'y': 'y',
    
    # Position 12: b
    'b': 'b',
    
    # Position 13: p
    'p': 'p',
    
    # Position 14: i (yod) — all Unicode variants
    'ꞽ': 'i',      # U+A7BD GLOTTAL I (primary)
    'i': 'i',
    'j': 'i',      # j often used for yod
    'ı': 'i',      # U+0131 dotless i
    'ỉ': 'i',      # U+1EC9 i with hook above
    
    # Position 15: kh (velar fricative)
    'ḫ': 'kh',     # U+1E2B h with breve below
    'ẖ': 'kh',     # U+1E96 h with line below
    'x': 'kh',     # x sometimes used for kh
    
    # Position 16: dj (palatalized) — on wheel
    'ḏ': 'dj',     # U+1E0F d with line below
    'ḍ': 'dj',     # U+1E0D d with dot below
    
    # SPINE phonemes (map but flag as spine)
    'd': 'd',      # Plain d is spine
    'k': 'k',      # Plain k is spine
    'q': 'k',      # Emphatic k → k (spine)
    'g': 'g',      # Spine
    'f': 'f',      # Spine
    'h': 'h',      # Glottal h is spine (distinct from pharyngeal H)
}

# All verbs (wheel + spine)
ALL_VERBS = {**WHEEL_VERBS, **SPINE_VERBS}

# Vowel markers for mode detection (used by engine.py)
VOWEL_MARKERS = {
    'a': 'masc',   # "ah" → masculine
    'e': 'fem',    # "ey/ay" → feminine
    'i': 'fem',    # → feminine
    'o': 'masc',   # → masculine
    'u': 'masc',   # → masculine
    'y': 'fem',    # → feminine
}

# Characters to skip (combining diacritics, grammatical markers handled in cleaning)
SKIP_CHARS = {
    '\u032f',  # U+032F COMBINING INVERTED BREVE BELOW
    '\u0331',  # U+0331 COMBINING MACRON BELOW
}


def leiden_to_wheel(translit: str, keep_words: bool = False) -> List[str]:
    """
    Convert Leiden transliteration to phoneme sequence.
    
    Returns both wheel AND spine phonemes (caller can distinguish).
    
    Args:
        translit: Leiden transliteration string
        keep_words: If True, return list of word-phoneme pairs
                   If False, return flat phoneme list
    
    Returns:
        List of phonemes (wheel + spine)
    """
    # Clean: remove parentheses content, =suffixes, punctuation, numbers
    # Also remove grammatical markers like .PL (plural) and .DU (dual)
    clean = re.sub(r'\([^)]*\)', '', translit)  # remove (...)
    clean = re.sub(r'=[a-zꞽꜣꜥ]+', '', clean)    # remove =sn, =f etc  
    clean = re.sub(r'\.(PL|DU|SG)', '', clean)  # remove .PL, .DU, .SG markers
    clean = re.sub(r'[.:\-+~0-9/!]', '', clean)  # remove punctuation
    clean = re.sub(r'[𓍹𓍺]', '', clean)          # remove cartouche markers
    clean = clean.lower().strip()
    
    if keep_words:
        words = clean.split()
        result = []
        for word in words:
            phonemes = _convert_word(word)
            if phonemes:
                result.append((word, phonemes))
        return result
    else:
        return _convert_word(clean.replace(' ', ''))


def _convert_word(word: str) -> List[str]:
    """Convert a single word to phonemes."""
    result = []
    for char in word:
        # Skip combining diacritics and whitespace
        if char in SKIP_CHARS or char in ' ':
            continue
        if char in LEIDEN_TO_WHEEL:
            result.append(LEIDEN_TO_WHEEL[char])
    return result


def is_wheel_phoneme(p: str) -> bool:
    """Check if phoneme is on the wheel."""
    return p in WHEEL_VERBS


def is_spine_phoneme(p: str) -> bool:
    """Check if phoneme is spine."""
    return p in SPINE_VERBS


def phonemes_to_verbs(phonemes: List[str]) -> List[str]:
    """Convert phoneme sequence to verb sequence."""
    return [ALL_VERBS.get(p, f'?{p}') for p in phonemes]


def wheel_trajectory(translit: str) -> str:
    """
    Generate a semantic trajectory from transliteration.
    
    Returns a human-readable verb chain.
    """
    phonemes = leiden_to_wheel(translit)
    verbs = phonemes_to_verbs(phonemes)
    return ' → '.join(verbs)
