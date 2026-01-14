"""
Phonemic Engine: The 408 Grammar

Core architecture:
- 16 wheel phonemes × 5 positions (hourglass) = 80 meaning-positions
- 3 spine phonemes (x, d, k) = the scales themselves
- T(16) = 136 unique wheel relations (including self-relations)
- Total grammar: 136 × 3 = 408 relations

The hourglass structure per phoneme:
        Masc Max
           △
          / \\
         / EQ \\   ← shared equilibrium
        /_____\\
        Fem Max
           ▽

The spine phonemes ARE the scales:
- k (ontogenic) = individual cycle
- d (phylogenic) = species action
- x (cosmogenic) = universal fundament
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional, Iterator
from itertools import combinations_with_replacement


class Mode(Enum):
    """Vowel-determined mode: masculine (ah) or feminine (ay/aleph)."""
    MASCULINE = "masc"
    FEMININE = "fem"


class Pole(Enum):
    """Position within the hourglass triangle."""
    MINIMA = "min"
    EQUILIBRIUM = "eq"
    MAXIMA = "max"


class SpinePhoneme(Enum):
    """
    The spine phonemes that define scales.
    
    These are wheel-ABSENT phonemes preserved in decan names.
    They frame the wheel while it rotates.
    """
    K = ('k', 'CYCLE', 5)       # Ontogenic - individual
    D = ('d', 'DO', 10)         # Phylogenic - species
    X = ('x', 'FUNDAMENT', 17)  # Cosmogenic - universal
    
    def __init__(self, phoneme: str, verb: str, decan_count: int):
        self._phoneme = phoneme
        self._verb = verb
        self._decan_count = decan_count
    
    @property
    def phoneme(self) -> str:
        return self._phoneme
    
    @property
    def verb(self) -> str:
        return self._verb
    
    @property
    def decan_count(self) -> int:
        """Number of occurrences in 37 decans."""
        return self._decan_count


class Scale(Enum):
    """
    Reading scope, linked to spine phonemes.
    
    The scales ARE phonemes: x, d, k
    """
    ONTOGENIC = SpinePhoneme.K    # Individual (my weaving)
    PHYLOGENIC = SpinePhoneme.D   # Species (woman weaves men)
    COSMOGENIC = SpinePhoneme.X   # Cosmic (Neith)
    
    @property
    def spine(self) -> SpinePhoneme:
        return self.value
    
    @property
    def phoneme(self) -> str:
        return self.value.phoneme
    
    @property
    def verb(self) -> str:
        return self.value.verb


# Spine phoneme constants
SPINE_PRIMARY = ['x', 'd', 'k']  # Primary spine (by decan frequency: 17, 10, 5)
SPINE_SECONDARY = ['q', 'tj', 'g', 'f', 'h']  # Emphatic/palatal variants + glottal h
SPINE_ALL = SPINE_PRIMARY + SPINE_SECONDARY


@dataclass
class Hourglass:
    """
    The 5-position meaning structure for a single phoneme.
    
    Two triangles touching at shared equilibrium:
    - Masculine: min_m, eq (shared), max_m
    - Feminine: min_f, eq (shared), max_f
    """
    phoneme: str
    deity: str
    
    # Core verb (equilibrium shared between modes)
    equilibrium_masc: str
    equilibrium_fem: str
    
    # Masculine poles
    min_masc: str
    max_masc: str
    
    # Feminine poles
    min_fem: str
    max_fem: str
    
    def get_meaning(self, mode: Mode, pole: Pole) -> str:
        """Get meaning for a specific mode and pole."""
        if pole == Pole.EQUILIBRIUM:
            return self.equilibrium_masc if mode == Mode.MASCULINE else self.equilibrium_fem
        elif mode == Mode.MASCULINE:
            return self.min_masc if pole == Pole.MINIMA else self.max_masc
        else:
            return self.min_fem if pole == Pole.MINIMA else self.max_fem
    
    @property
    def core_verb(self) -> str:
        """The primary verb (masculine equilibrium by convention)."""
        return self.equilibrium_masc


# The complete 16-phoneme hourglass lexicon (WHEEL phonemes) - v63
PHONEME_HOURGLASSES: Dict[str, Hourglass] = {
    # Position 1: n
    'n': Hourglass(
        phoneme='n', deity='Neith',
        equilibrium_masc='INTEGRATE', equilibrium_fem='WEAVE',
        min_masc='FRAGMENT', max_masc='FUSE',
        min_fem='UNRAVEL', max_fem='INTERLOCK'
    ),
    # Position 2: w
    'w': Hourglass(
        phoneme='w', deity='Wadjet',
        equilibrium_masc='RADIATE', equilibrium_fem='FLOW',
        min_masc='CONTAIN', max_masc='FLOOD',
        min_fem='STAGNATE', max_fem='CIRCULATE'
    ),
    # Position 3: s
    's': Hourglass(
        phoneme='s', deity='Sekhmet',
        equilibrium_masc='EMERGE', equilibrium_fem='CRYSTALLISE',
        min_masc='REGRESS', max_masc='BURST',
        min_fem='EXPOSE', max_fem='ENCASE'
    ),
    # Position 4: sh
    'sh': Hourglass(
        phoneme='sh', deity='Shu',
        equilibrium_masc='DIRECT', equilibrium_fem='ALIGN',
        min_masc='SCATTER', max_masc='COMMAND',
        min_fem='DRIFT', max_fem='ORIENT'
    ),
    # Position 5: A (aleph - glottal stop)
    'A': Hourglass(
        phoneme='A', deity='Atum',
        equilibrium_masc='LEAD', equilibrium_fem='TEND',
        min_masc='ABANDON', max_masc='DRIVE',
        min_fem='NEGLECT', max_fem='NURTURE'
    ),
    # Position 6: t
    't': Hourglass(
        phoneme='t', deity='Seshat',
        equilibrium_masc='READ', equilibrium_fem='ETCH',
        min_masc='MISREAD', max_masc='DECODE',
        min_fem='ERASE', max_fem='INSCRIBE'
    ),
    # Position 7: H (pharyngeal)
    'H': Hourglass(
        phoneme='H', deity='Horus',
        equilibrium_masc='EXPRESS', equilibrium_fem='INTERPRET',
        min_masc='SUPPRESS', max_masc='PROCLAIM',
        min_fem='MISREAD', max_fem='COMPREHEND'
    ),
    # Position 8: r
    'r': Hourglass(
        phoneme='r', deity='Ra',
        equilibrium_masc='SHINE', equilibrium_fem='BASK',
        min_masc='DIM', max_masc='BLAZE',
        min_fem='SHADE', max_fem='ABSORB'
    ),
    # Position 9: m
    'm': Hourglass(
        phoneme='m', deity="Ma'at",
        equilibrium_masc='TRUE', equilibrium_fem='TRUST',
        min_masc='FALSIFY', max_masc='VERIFY',
        min_fem='DOUBT', max_fem='BELIEVE'
    ),
    # Position 10: a (ayin)
    'a': Hourglass(
        phoneme='a', deity='Anubis',
        equilibrium_masc='HONOUR', equilibrium_fem='ALLOW',
        min_masc='DISHONOUR', max_masc='REVERE',
        min_fem='BLOCK', max_fem='PERMIT'
    ),
    # Position 11: y
    'y': Hourglass(
        phoneme='y', deity='Isis',
        equilibrium_masc='DEVOTE', equilibrium_fem='RESTORE',
        min_masc='BETRAY', max_masc='CONSECRATE',
        min_fem='NEGLECT', max_fem='HEAL'
    ),
    # Position 12: b
    'b': Hourglass(
        phoneme='b', deity='Bes',
        equilibrium_masc='RECEIVE', equilibrium_fem='CULTIVATE',
        min_masc='REFUSE', max_masc='ENGULF',
        min_fem='DEPLETE', max_fem='NOURISH'
    ),
    # Position 13: p
    'p': Hourglass(
        phoneme='p', deity='Ptah',
        equilibrium_masc='STORE', equilibrium_fem='GATHER',
        min_masc='SCATTER', max_masc='HOARD',
        min_fem='DISPERSE', max_fem='COLLECT'
    ),
    # Position 14: i (yod)
    'i': Hourglass(
        phoneme='i', deity='Ihy',
        equilibrium_masc='BESTOW', equilibrium_fem='PROTECT',
        min_masc='WITHHOLD', max_masc='GIFT',
        min_fem='EXPOSE', max_fem='GUARD'
    ),
    # Position 15: kh
    'kh': Hourglass(
        phoneme='kh', deity='Khnum',
        equilibrium_masc='EMBODY', equilibrium_fem='CAPACITY',
        min_masc='FUMBLE', max_masc='MASTER',
        min_fem='NUMB', max_fem='DEFT'
    ),
    # Position 16: dj (palatalized)
    'dj': Hourglass(
        phoneme='dj', deity='Thoth',
        equilibrium_masc='DISCERN', equilibrium_fem='ACT',
        min_masc='CONFUSE', max_masc='PERCEIVE',
        min_fem='HESITATE', max_fem='EXECUTE'
    ),
}

# SPINE phoneme hourglasses (for decoding texts containing spine phonemes)
SPINE_HOURGLASSES: Dict[str, Hourglass] = {
    'd': Hourglass(
        phoneme='d', deity='Duat',
        equilibrium_masc='DO', equilibrium_fem='MIDWIFE',
        min_masc='STALL', max_masc='FORCE',
        min_fem='WAIT', max_fem='COMPLETE'
    ),
    'k': Hourglass(
        phoneme='k', deity='Ka/Khonsu',
        equilibrium_masc='CYCLE', equilibrium_fem='RETURN',
        min_masc='HALT', max_masc='ACCELERATE',
        min_fem='REST', max_fem='REUNITE'
    ),
    'h': Hourglass(
        phoneme='h', deity='Horus',
        equilibrium_masc='SEE', equilibrium_fem='WITNESS',
        min_masc='BLIND', max_masc='PIERCE',
        min_fem='IGNORE', max_fem='BEHOLD'
    ),
    'g': Hourglass(
        phoneme='g', deity='Geb',
        equilibrium_masc='GROUND', equilibrium_fem='STABILIZE',
        min_masc='FLOAT', max_masc='SINK',
        min_fem='UNROOT', max_fem='ANCHOR'
    ),
    'f': Hourglass(
        phoneme='f', deity='—',
        equilibrium_masc='BREATHE', equilibrium_fem='FLOW',
        min_masc='CHOKE', max_masc='FLOOD',
        min_fem='STILL', max_fem='SURGE'
    ),
    'x': Hourglass(
        phoneme='x', deity='—',
        equilibrium_masc='FUNDAMENT', equilibrium_fem='FOUNDATION',
        min_masc='DISSOLVE', max_masc='PETRIFY',
        min_fem='RELEASE', max_fem='ANCHOR'
    ),
}

# All hourglasses (wheel + spine)
ALL_HOURGLASSES: Dict[str, Hourglass] = {**PHONEME_HOURGLASSES, **SPINE_HOURGLASSES}

# Ordered list of WHEEL phonemes (for relation generation)
WHEEL_PHONEMES = ['n', 'w', 's', 'sh', 'A', 't', 'H', 'r', 'm', 'a', 'y', 'b', 'p', 'i', 'kh', 'dj']
PHONEME_ORDER = WHEEL_PHONEMES  # Alias for backward compatibility


def get_hourglass(phoneme: str) -> Optional[Hourglass]:
    """Get the hourglass structure for a phoneme (wheel or spine)."""
    return ALL_HOURGLASSES.get(phoneme)


def get_core_verb(phoneme: str) -> str:
    """Get the core verb (masculine equilibrium) for a phoneme."""
    hg = get_hourglass(phoneme)
    return hg.core_verb if hg else f'?{phoneme}'


def triangular(n: int) -> int:
    """Calculate triangular number T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


def generate_relations() -> List[Tuple[str, str]]:
    """
    Generate all 136 unique phoneme pairs INCLUDING self-relations.
    
    T(16) = 16 + 15 + 14 + ... + 1 = 136
    
    This includes:
    - 16 self-relations (A-A, B-B, etc.)
    - 120 distinct pairs (A-B, A-C, etc.)
    
    Total: 136
    """
    # combinations_with_replacement gives us pairs including (a,a), (b,b), etc.
    return list(combinations_with_replacement(WHEEL_PHONEMES, 2))


def count_relations() -> int:
    """
    Return T(16) = 136.
    
    This is the 16th triangular number, counting:
    - All self-relations (16)
    - All distinct pairs (120)
    """
    return triangular(16)


def get_all_relations() -> List['Relation']:
    """Get all 136 phoneme relations."""
    return [Relation(a, b) for a, b in generate_relations()]


def total_grammar() -> int:
    """
    Total grammar = 136 relations × 3 scales = 408.
    
    Each wheel relation exists in 3 versions (through each spine axis).
    """
    return count_relations() * len(Scale)


@dataclass
class Relation:
    """
    A grammatical relation between two phonemes.
    
    Basic relation (wheel × wheel).
    For full triangular relation, use TriangularRelation.
    """
    phoneme_a: str
    phoneme_b: str
    
    @property
    def is_self_relation(self) -> bool:
        """True if both phonemes are the same."""
        return self.phoneme_a == self.phoneme_b
    
    @property
    def verb_a(self) -> str:
        return get_core_verb(self.phoneme_a)
    
    @property
    def verb_b(self) -> str:
        return get_core_verb(self.phoneme_b)
    
    @property
    def forward(self) -> str:
        """A → B reading."""
        return f"{self.verb_a}→{self.verb_b}"
    
    @property
    def reverse(self) -> str:
        """B → A reading."""
        return f"{self.verb_b}→{self.verb_a}"


@dataclass
class TriangularRelation:
    """
    A complete grammatical relation: two wheel phonemes + one spine axis.
    
    This is the fundamental unit of the 408 grammar:
    
            A (wheel)
           /|\\
          / | \\
         x  d  k    ← spine determines scale
          \\ | /
           \\|/
            B (wheel)
    """
    phoneme_a: str
    phoneme_b: str
    scale: Scale
    
    @property
    def spine_phoneme(self) -> str:
        """The spine phoneme that defines this relation's scale."""
        return self.scale.phoneme
    
    @property
    def spine_verb(self) -> str:
        """The verb of the spine phoneme."""
        return self.scale.verb
    
    @property
    def is_self_relation(self) -> bool:
        """True if both wheel phonemes are the same."""
        return self.phoneme_a == self.phoneme_b
    
    @property
    def verb_a(self) -> str:
        return get_core_verb(self.phoneme_a)
    
    @property
    def verb_b(self) -> str:
        return get_core_verb(self.phoneme_b)
    
    @property
    def description(self) -> str:
        """Human-readable description of the relation."""
        scale_name = self.scale.name.lower()
        if self.is_self_relation:
            return f"{self.verb_a} ({scale_name})"
        return f"{self.verb_a}↔{self.verb_b} ({scale_name})"


def generate_all_triangular_relations() -> Iterator[TriangularRelation]:
    """
    Generate all 408 triangular relations.
    
    Each of the 136 wheel relations × 3 spine scales = 408 total.
    """
    for a, b in generate_relations():
        for scale in Scale:
            yield TriangularRelation(a, b, scale)


def get_all_triangular_relations() -> List[TriangularRelation]:
    """Get all 408 triangular relations as a list."""
    return list(generate_all_triangular_relations())


def count_triangular_relations() -> int:
    """Return 408 (the complete grammar)."""
    return total_grammar()


# Verification assertions
assert len(WHEEL_PHONEMES) == 16, f"Expected 16 wheel phonemes, got {len(WHEEL_PHONEMES)}"
assert triangular(16) == 136, f"T(16) should be 136, got {triangular(16)}"
assert count_relations() == 136, f"Should have 136 relations, got {count_relations()}"
assert len(Scale) == 3, f"Expected 3 scales, got {len(Scale)}"
assert total_grammar() == 408, f"Total grammar should be 408, got {total_grammar()}"


# Vowel → Mode mapping
MASCULINE_VOWELS = {'a', 'o', 'u'}  # "ah" and stress markers → masculine
FEMININE_MARKERS = {'e', 'i', 'y', 'ꜣ', 'ꞽ'}  # "ay/ey" aleph forms → feminine


def detect_mode(vowel: str) -> Mode:
    """Determine mode from vowel sound."""
    if vowel.lower() in FEMININE_MARKERS:
        return Mode.FEMININE
    return Mode.MASCULINE  # Default to masculine


def decode_with_mode(
    phonemes: List[str],
    mode: Mode = Mode.MASCULINE,
    pole: Pole = Pole.EQUILIBRIUM,
    scale: Scale = Scale.ONTOGENIC
) -> List[str]:
    """
    Decode a phoneme sequence with explicit mode and pole.
    
    Args:
        phonemes: List of wheel phonemes
        mode: Masculine or feminine mode
        pole: Which position in the hourglass
        scale: Reading scope (affects interpretation context)
    
    Returns:
        List of verb meanings
    """
    result = []
    for p in phonemes:
        hg = get_hourglass(p)
        if hg:
            meaning = hg.get_meaning(mode, pole)
            result.append(meaning)
        else:
            result.append(f'?{p}')
    return result


def decode_trajectory(
    phonemes: List[str],
    mode: Mode = Mode.MASCULINE,
    pole: Pole = Pole.EQUILIBRIUM
) -> str:
    """Get human-readable trajectory string."""
    verbs = decode_with_mode(phonemes, mode, pole)
    return ' → '.join(verbs)


# Convenience functions for backward compatibility
def phonemes_to_verbs(phonemes: List[str]) -> List[str]:
    """Convert phoneme sequence to core verbs (masculine equilibrium)."""
    return [get_core_verb(p) for p in phonemes]


def is_wheel_phoneme(phoneme: str) -> bool:
    """Check if a phoneme is in the wheel (transmissible set)."""
    return phoneme in WHEEL_PHONEMES


def is_spine_phoneme(phoneme: str) -> bool:
    """Check if a phoneme is in the spine (frame/scale set)."""
    return phoneme in SPINE_ALL


def classify_phoneme(phoneme: str) -> str:
    """Classify a phoneme as wheel, spine-primary, spine-secondary, or unknown."""
    if phoneme in WHEEL_PHONEMES:
        return 'wheel'
    elif phoneme in SPINE_PRIMARY:
        return 'spine-primary'
    elif phoneme in SPINE_SECONDARY:
        return 'spine-secondary'
    return 'unknown'
