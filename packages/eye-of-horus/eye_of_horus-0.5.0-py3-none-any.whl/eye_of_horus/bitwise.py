"""
Bitwise Phonemic Engine

8-bit semantic addressing for high-performance phoneme processing.

Address format: [5 bits phoneme][3 bits position]
- Phoneme: 0-15 = wheel, 16-21 = spine
- Position: [1 bit mode][2 bits pole]

Enables vectorized decode of entire texts via array indexing.
"""

import numpy as np
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import IntEnum

# =============================================================================
# PHONEME IDs (5 bits: 0-21)
# =============================================================================

# Wheel phonemes (0-15)
ID_N  = 0
ID_W  = 1
ID_S  = 2
ID_SH = 3
ID_A  = 4   # Aleph
ID_T  = 5
ID_H  = 6   # Pharyngeal
ID_R  = 7
ID_M  = 8
ID_AA = 9   # Ayin
ID_Y  = 10
ID_B  = 11
ID_P  = 12
ID_I  = 13  # Yod
ID_KH = 14
ID_DJ = 15

# Spine phonemes (16-21)
ID_D  = 16
ID_K  = 17
ID_X  = 18
ID_G  = 19
ID_F  = 20
ID_HH = 21  # Glottal h (distinct from pharyngeal H)

# Classification mask
SPINE_BIT = 0b10000  # Bit 4 set = spine phoneme

# =============================================================================
# POSITION ENCODING (3 bits)
# =============================================================================

class Pos(IntEnum):
    """Hourglass position as 3-bit encoding."""
    EQ_MASC  = 0b000  # Masculine equilibrium (core)
    MIN_MASC = 0b001  # Masculine minimum
    MAX_MASC = 0b010  # Masculine maximum
    EQ_FEM   = 0b100  # Feminine equilibrium
    MIN_FEM  = 0b101  # Feminine minimum
    MAX_FEM  = 0b110  # Feminine maximum


# Mode bit
MODE_MASC = 0
MODE_FEM  = 1
MODE_MASK = 0b100

# Pole bits
POLE_EQ  = 0b00
POLE_MIN = 0b01
POLE_MAX = 0b10
POLE_MASK = 0b011

# =============================================================================
# LAYER ENCODING
# =============================================================================

class Layer(IntEnum):
    """The 5 decode layers."""
    CORE = 0  # All equilibrium
    F1   = 1  # Feminine minima
    F2   = 2  # Feminine maxima
    M1   = 3  # Masculine minima
    M2   = 4  # Masculine maxima


# Layer → position bits (at pole positions; eq at alternating positions)
LAYER_POS = np.array([
    Pos.EQ_MASC,   # CORE: all eq (mode arbitrary, pole = 0)
    Pos.MIN_FEM,   # F1
    Pos.MAX_FEM,   # F2
    Pos.MIN_MASC,  # M1
    Pos.MAX_MASC,  # M2
], dtype=np.uint8)

# =============================================================================
# PHONEME MAPPINGS
# =============================================================================

# String → ID (for initial parse)
PHONEME_TO_ID = {
    # Wheel
    'n': ID_N, 'w': ID_W, 's': ID_S, 'sh': ID_SH,
    'A': ID_A, 't': ID_T, 'H': ID_H, 'r': ID_R,
    'm': ID_M, 'a': ID_AA, 'y': ID_Y, 'b': ID_B,
    'p': ID_P, 'i': ID_I, 'kh': ID_KH, 'dj': ID_DJ,
    # Spine
    'd': ID_D, 'k': ID_K, 'x': ID_X,
    'g': ID_G, 'f': ID_F, 'h': ID_HH,
}

# ID → string (for output)
ID_TO_PHONEME = np.array([
    'n', 'w', 's', 'sh', 'A', 't', 'H', 'r',
    'm', 'a', 'y', 'b', 'p', 'i', 'kh', 'dj',
    'd', 'k', 'x', 'g', 'f', 'h',
])

NUM_PHONEMES = 22
NUM_WHEEL = 16
NUM_SPINE = 6

# =============================================================================
# VERB TABLE (256 entries, indexed by semantic address)
# =============================================================================

# Verb data (v63): phoneme_id → (eq_m, min_m, max_m, eq_f, min_f, max_f)
_VERB_DATA = {
    # Wheel phonemes (v62 lexicon)
    ID_N:  ('INTEGRATE', 'FRAGMENT', 'FUSE', 'WEAVE', 'UNRAVEL', 'INTERLOCK'),
    ID_W:  ('RADIATE', 'CONTAIN', 'FLOOD', 'FLOW', 'STAGNATE', 'CIRCULATE'),
    ID_S:  ('EMERGE', 'REGRESS', 'BURST', 'CRYSTALLISE', 'EXPOSE', 'ENCASE'),
    ID_SH: ('DIRECT', 'SCATTER', 'COMMAND', 'ALIGN', 'DRIFT', 'ORIENT'),
    ID_A:  ('LEAD', 'ABANDON', 'DRIVE', 'TEND', 'NEGLECT', 'NURTURE'),
    ID_T:  ('READ', 'MISREAD', 'DECODE', 'ETCH', 'ERASE', 'INSCRIBE'),
    ID_H:  ('EXPRESS', 'SUPPRESS', 'PROCLAIM', 'INTERPRET', 'MISREAD', 'COMPREHEND'),
    ID_R:  ('SHINE', 'DIM', 'BLAZE', 'BASK', 'SHADE', 'ABSORB'),
    ID_M:  ('TRUE', 'FALSIFY', 'VERIFY', 'TRUST', 'DOUBT', 'BELIEVE'),
    ID_AA: ('HONOUR', 'DISHONOUR', 'REVERE', 'ALLOW', 'BLOCK', 'PERMIT'),
    ID_Y:  ('DEVOTE', 'BETRAY', 'CONSECRATE', 'RESTORE', 'NEGLECT', 'HEAL'),
    ID_B:  ('RECEIVE', 'REFUSE', 'ENGULF', 'CULTIVATE', 'DEPLETE', 'NOURISH'),
    ID_P:  ('STORE', 'SCATTER', 'HOARD', 'GATHER', 'DISPERSE', 'COLLECT'),
    ID_I:  ('BESTOW', 'WITHHOLD', 'GIFT', 'PROTECT', 'EXPOSE', 'GUARD'),
    ID_KH: ('EMBODY', 'FUMBLE', 'MASTER', 'CAPACITY', 'NUMB', 'DEFT'),
    ID_DJ: ('DISCERN', 'CONFUSE', 'PERCEIVE', 'ACT', 'HESITATE', 'EXECUTE'),
    # Spine phonemes
    ID_D:  ('DO', 'STALL', 'FORCE', 'MIDWIFE', 'WAIT', 'COMPLETE'),
    ID_K:  ('CYCLE', 'HALT', 'ACCELERATE', 'RETURN', 'REST', 'REUNITE'),
    ID_X:  ('FUNDAMENT', 'DISSOLVE', 'PETRIFY', 'FOUNDATION', 'RELEASE', 'ANCHOR'),
    ID_G:  ('GROUND', 'FLOAT', 'SINK', 'STABILIZE', 'UNROOT', 'ANCHOR'),
    ID_F:  ('BREATHE', 'CHOKE', 'FLOOD', 'FLOW', 'STILL', 'SURGE'),
    ID_HH: ('SEE', 'BLIND', 'PIERCE', 'WITNESS', 'IGNORE', 'BEHOLD'),
}

# Build the 256-entry lookup table
VERB_TABLE = np.empty(256, dtype='U16')
VERB_TABLE[:] = ''  # Initialize empty

for phoneme_id, verbs in _VERB_DATA.items():
    eq_m, min_m, max_m, eq_f, min_f, max_f = verbs
    # Map position bits to verb
    VERB_TABLE[(phoneme_id << 3) | Pos.EQ_MASC]  = eq_m
    VERB_TABLE[(phoneme_id << 3) | Pos.MIN_MASC] = min_m
    VERB_TABLE[(phoneme_id << 3) | Pos.MAX_MASC] = max_m
    VERB_TABLE[(phoneme_id << 3) | Pos.EQ_FEM]   = eq_f
    VERB_TABLE[(phoneme_id << 3) | Pos.MIN_FEM]  = min_f
    VERB_TABLE[(phoneme_id << 3) | Pos.MAX_FEM]  = max_f

# =============================================================================
# CORE VERB TABLE (equilibrium only, for simple lookups) - v63
# =============================================================================

CORE_VERB_TABLE = np.array([
    'INTEGRATE', 'RADIATE', 'EMERGE', 'DIRECT', 'LEAD', 'READ', 'EXPRESS', 'SHINE',
    'TRUE', 'HONOUR', 'DEVOTE', 'RECEIVE', 'STORE', 'BESTOW', 'EMBODY', 'DISCERN',
    'DO', 'CYCLE', 'FUNDAMENT', 'GROUND', 'BREATHE', 'SEE',
])

# =============================================================================
# ENCODING FUNCTIONS
# =============================================================================

def encode_phonemes(phonemes: List[str]) -> np.ndarray:
    """
    Convert phoneme string list to ID array.
    
    Args:
        phonemes: List of phoneme strings ('n', 'w', 'sh', etc.)
    
    Returns:
        uint8 array of phoneme IDs
    """
    return np.array([PHONEME_TO_ID[p] for p in phonemes], dtype=np.uint8)


def decode_ids(ids: np.ndarray) -> List[str]:
    """Convert ID array back to phoneme strings."""
    return [ID_TO_PHONEME[i] for i in ids]


def semantic_address(phoneme_id: int, mode: int, pole: int) -> int:
    """
    Compute 8-bit semantic address.
    
    Args:
        phoneme_id: 0-21 phoneme ID
        mode: 0=masculine, 1=feminine
        pole: 0=eq, 1=min, 2=max
    
    Returns:
        8-bit address for VERB_TABLE lookup
    """
    return (phoneme_id << 3) | (mode << 2) | pole


def address_to_components(address: int) -> Tuple[int, int, int]:
    """
    Decompose semantic address.
    
    Returns:
        (phoneme_id, mode, pole)
    """
    phoneme_id = address >> 3
    mode = (address >> 2) & 1
    pole = address & 0b011
    return phoneme_id, mode, pole


# =============================================================================
# CLASSIFICATION
# =============================================================================

def is_wheel(phoneme_id: int) -> bool:
    """Check if phoneme ID is wheel (0-15)."""
    return (phoneme_id & SPINE_BIT) == 0


def is_spine(phoneme_id: int) -> bool:
    """Check if phoneme ID is spine (16-21)."""
    return (phoneme_id & SPINE_BIT) != 0


def is_wheel_array(ids: np.ndarray) -> np.ndarray:
    """Vectorized wheel classification."""
    return (ids & SPINE_BIT) == 0


def is_spine_array(ids: np.ndarray) -> np.ndarray:
    """Vectorized spine classification."""
    return (ids & SPINE_BIT) != 0


# =============================================================================
# LAYERED DECODE (VECTORIZED)
# =============================================================================

def decode_layer(phoneme_ids: np.ndarray, layer: int) -> np.ndarray:
    """
    Decode phoneme array through a single layer.
    
    Args:
        phoneme_ids: uint8 array of phoneme IDs
        layer: 0=core, 1=f1, 2=f2, 3=m1, 4=m2
    
    Returns:
        Array of verb strings
    """
    layer_pos = LAYER_POS[layer]
    
    if layer == Layer.CORE:
        # Core layer: all equilibrium (mode doesn't matter, pole=0)
        addresses = (phoneme_ids.astype(np.int32) << 3) | Pos.EQ_MASC
    else:
        # Extract mode and pole from layer
        layer_mode = (layer_pos >> 2) & 1
        layer_pole = layer_pos & POLE_MASK
        
        # Alternation: pole at even indices, eq at odd
        n = len(phoneme_ids)
        indices = np.arange(n)
        use_pole = (indices & 1) == 0  # Even positions get pole
        
        # Build position bits
        poles = np.where(use_pole, layer_pole, POLE_EQ)
        pos_bits = (layer_mode << 2) | poles
        
        addresses = (phoneme_ids.astype(np.int32) << 3) | pos_bits
    
    return VERB_TABLE[addresses]


def decode_all_layers(phoneme_ids: np.ndarray) -> List[np.ndarray]:
    """
    Decode phoneme array through all 5 layers.
    
    Returns:
        List of 5 verb arrays [core, f1, f2, m1, m2]
    """
    return [decode_layer(phoneme_ids, layer) for layer in range(5)]


@dataclass
class LayeredResult:
    """Result of layered decode."""
    core: np.ndarray
    f1: np.ndarray
    f2: np.ndarray
    m1: np.ndarray
    m2: np.ndarray
    phoneme_ids: np.ndarray
    
    def as_dict(self) -> dict:
        return {
            'core': self.core,
            'f1': self.f1,
            'f2': self.f2,
            'm1': self.m1,
            'm2': self.m2,
        }
    
    def to_strings(self) -> dict:
        """Convert all layers to lists of strings."""
        return {
            'core': self.core.tolist(),
            'f1': self.f1.tolist(),
            'f2': self.f2.tolist(),
            'm1': self.m1.tolist(),
            'm2': self.m2.tolist(),
        }


def decode_layered(phoneme_ids: np.ndarray) -> LayeredResult:
    """
    Full layered decode returning structured result.
    """
    layers = decode_all_layers(phoneme_ids)
    return LayeredResult(
        core=layers[0],
        f1=layers[1],
        f2=layers[2],
        m1=layers[3],
        m2=layers[4],
        phoneme_ids=phoneme_ids,
    )


# =============================================================================
# RELATION ENCODING (10 bits for wheel pairs)
# =============================================================================

def relation_index(a: int, b: int) -> int:
    """
    Compute triangular relation index for two wheel phonemes.
    
    Uses canonical ordering (a ≤ b).
    T(b) + a gives index 0-135.
    """
    if a > b:
        a, b = b, a
    return (b * (b + 1) >> 1) + a


def relation_to_pair(index: int) -> Tuple[int, int]:
    """
    Reverse triangular index to phoneme pair.
    """
    # Find b such that T(b) ≤ index < T(b+1)
    b = int((-1 + (1 + 8 * index) ** 0.5) // 2)
    a = index - (b * (b + 1) >> 1)
    return a, b


# Total relations
NUM_WHEEL_RELATIONS = 136  # T(16)

# =============================================================================
# GRAMMAR ENCODING (12 bits: scale + relation)
# =============================================================================

class Scale(IntEnum):
    """The 3 scales (spine axes)."""
    ONTOGENIC  = 0  # k
    PHYLOGENIC = 1  # d
    COSMOGENIC = 2  # x


def grammar_index(scale: int, relation: int) -> int:
    """Compute 408-grammar index."""
    return scale * NUM_WHEEL_RELATIONS + relation


def grammar_to_components(index: int) -> Tuple[int, int]:
    """Decompose grammar index to (scale, relation)."""
    scale = index // NUM_WHEEL_RELATIONS
    relation = index % NUM_WHEEL_RELATIONS
    return scale, relation


TOTAL_GRAMMAR = 408  # 3 scales × 136 relations

# =============================================================================
# CONVENIENCE: FROM STRING TO VERBS
# =============================================================================

def phonemes_to_verbs_fast(phonemes: List[str]) -> List[str]:
    """
    Fast path: phoneme strings → core verbs.
    """
    ids = encode_phonemes(phonemes)
    return CORE_VERB_TABLE[ids].tolist()


def decode_text(phonemes: List[str]) -> LayeredResult:
    """
    Full decode: phoneme strings → all 5 layers.
    """
    ids = encode_phonemes(phonemes)
    return decode_layered(ids)


# =============================================================================
# VERIFICATION
# =============================================================================

assert len(PHONEME_TO_ID) == NUM_PHONEMES
assert len(ID_TO_PHONEME) == NUM_PHONEMES
assert len(CORE_VERB_TABLE) == NUM_PHONEMES
assert (NUM_WHEEL * (NUM_WHEEL + 1) // 2) == NUM_WHEEL_RELATIONS
assert 3 * NUM_WHEEL_RELATIONS == TOTAL_GRAMMAR
