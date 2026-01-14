"""
Fibonacci Rhythm & Breath Module

Implements:
- Fibonacci boundary detection (clause/sentence breaks)
- Script health scoring (semantic integrity)
- Breath phase tracking (inhale/exhale/pivot)
"""

from enum import Enum
from typing import List, Dict, Tuple
import math


# Golden ratio
PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
PHI_INV = 1 / PHI             # 0.618033988749895


class BreathPhase(Enum):
    """Position in the cosmic breath cycle."""
    SEED = "seed"           # Unity, potential
    EXHALE = "exhale"       # Expansion, division
    PIVOT = "pivot"         # Turn point, peak manifestation
    INHALE = "inhale"       # Contraction, return
    RETURN = "return"       # Back to source


class ScriptHealth(Enum):
    """Semantic integrity based on script traceability."""
    HIEROGLYPH_ATTESTED = 3  # Full chain to pictographic source
    HIERATIC_ATTESTED = 2    # Partial chain (cursive)
    COPTIC_ONLY = 1          # Orphaned (divided)
    UNKNOWN = 0              # No attestation data


# Fibonacci sequence for reference
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


def fibonacci(n: int) -> int:
    """Return nth Fibonacci number (0-indexed)."""
    if n < len(FIBONACCI):
        return FIBONACCI[n]
    a, b = FIBONACCI[-2], FIBONACCI[-1]
    for _ in range(n - len(FIBONACCI) + 1):
        a, b = b, a + b
    return b


def detect_phi_boundaries(phoneme_count: int) -> List[int]:
    """
    Return clause boundary positions based on golden ratio.
    
    These mark where "sentences" or semantic units end.
    Works backwards from total using φ subdivision.
    
    Args:
        phoneme_count: Total phonemes in sequence
        
    Returns:
        List of boundary positions (0-indexed, exclusive)
    """
    if phoneme_count <= 1:
        return []
    
    boundaries = []
    remaining = phoneme_count
    position = 0
    
    while remaining > 2:
        # Subdivide by phi
        segment = int(remaining * PHI_INV)
        if segment < 1:
            break
        position += segment
        boundaries.append(position)
        remaining = remaining - segment
    
    return boundaries


def detect_yuga_boundaries(phoneme_count: int) -> Dict[str, Tuple[int, int]]:
    """
    Return Yuga-based clause boundaries (4:3:2:1 ratio).
    
    Args:
        phoneme_count: Total phonemes in sequence
        
    Returns:
        Dict mapping Yuga name to (start, end) positions
    """
    # 4 + 3 + 2 + 1 = 10 units
    unit = phoneme_count / 10
    
    return {
        'satya': (0, int(4 * unit)),
        'treta': (int(4 * unit), int(7 * unit)),
        'dvapara': (int(7 * unit), int(9 * unit)),
        'kali': (int(9 * unit), phoneme_count),
    }


def detect_breath_phase(line_number: int, total_lines: int = 9) -> BreathPhase:
    """
    Determine breath phase based on position in genesis block.
    
    The 9-line structure follows Fibonacci: 1 + 2 + 3 + 2 + 1 = 9
    
    Args:
        line_number: 1-indexed line number
        total_lines: Total lines in block (default 9)
        
    Returns:
        BreathPhase enum value
    """
    if total_lines != 9:
        # Generalize for other block sizes
        mid = total_lines // 2 + 1
        if line_number == 1:
            return BreathPhase.SEED
        elif line_number < mid:
            return BreathPhase.EXHALE
        elif line_number == mid:
            return BreathPhase.PIVOT
        elif line_number < total_lines:
            return BreathPhase.INHALE
        else:
            return BreathPhase.RETURN
    
    # Standard 9-line genesis block
    if line_number == 1:
        return BreathPhase.SEED
    elif line_number in (2, 3):
        return BreathPhase.EXHALE
    elif line_number in (4, 5, 6):
        return BreathPhase.PIVOT
    elif line_number in (7, 8):
        return BreathPhase.INHALE
    else:  # line 9
        return BreathPhase.RETURN


def score_script_health(
    hieroglyph_attested: bool = False,
    hieratic_attested: bool = False,
    coptic_attested: bool = False
) -> ScriptHealth:
    """
    Score a word's semantic integrity by script traceability.
    
    The breath ratio: Hieroglyph:Hieratic = 1:1, Hieratic:Coptic = 1:2
    
    Args:
        hieroglyph_attested: Word found in hieroglyphic texts
        hieratic_attested: Word found in hieratic texts
        coptic_attested: Word found in Coptic texts
        
    Returns:
        ScriptHealth score
    """
    if hieroglyph_attested:
        return ScriptHealth.HIEROGLYPH_ATTESTED
    elif hieratic_attested:
        return ScriptHealth.HIERATIC_ATTESTED
    elif coptic_attested:
        return ScriptHealth.COPTIC_ONLY
    return ScriptHealth.UNKNOWN


def get_fibonacci_line_structure() -> Dict[str, List[int]]:
    """
    Return the Fibonacci breath structure for 9-line blocks.
    
    Returns:
        Dict with phase names mapping to line numbers
    """
    return {
        'seed': [1],
        'exhale': [2, 3],
        'pivot': [4, 5, 6],
        'inhale': [7, 8],
        'return': [9],
    }


def is_at_phi_boundary(position: int, total: int, tolerance: float = 0.5) -> bool:
    """
    Check if a position is at a golden ratio boundary.
    
    Args:
        position: Current position (0-indexed)
        total: Total length
        tolerance: How close to boundary counts (in positions)
        
    Returns:
        True if at a phi boundary
    """
    boundaries = detect_phi_boundaries(total)
    for b in boundaries:
        if abs(position - b) <= tolerance:
            return True
    return False


def segment_by_fibonacci(sequence: List, max_segments: int = 5) -> List[List]:
    """
    Segment a sequence according to Fibonacci ratios.
    
    Args:
        sequence: List of items to segment
        max_segments: Maximum number of segments
        
    Returns:
        List of sub-lists
    """
    if not sequence:
        return []
    
    boundaries = detect_phi_boundaries(len(sequence))
    boundaries = boundaries[:max_segments - 1]  # Limit segments
    
    segments = []
    prev = 0
    for b in boundaries:
        segments.append(sequence[prev:b])
        prev = b
    segments.append(sequence[prev:])  # Final segment
    
    return [s for s in segments if s]  # Remove empty


def analyze_line_rhythm(phonemes: List[str]) -> Dict:
    """
    Analyze the rhythm structure of a phoneme sequence.
    
    Returns:
        Dict with phi boundaries, yuga boundaries, and analysis
    """
    count = len(phonemes)
    
    phi_bounds = detect_phi_boundaries(count)
    yuga_bounds = detect_yuga_boundaries(count)
    
    # Segment by phi
    segments = segment_by_fibonacci(phonemes)
    
    return {
        'total_phonemes': count,
        'phi_boundaries': phi_bounds,
        'yuga_boundaries': yuga_bounds,
        'phi_segments': segments,
        'segment_sizes': [len(s) for s in segments],
    }


# Script breath ratios (for documentation)
SCRIPT_RATIOS = {
    'hieroglyph_to_hieratic': (1, 1),  # Unity maintained
    'hieratic_to_coptic': (1, 2),       # Division begins
    'sequence': [1, 1, 2],              # Fibonacci seed
}
