"""
Pyramid Texts decoder using the 16-position wheel.

The Pyramid Texts of Unas (~2375-2345 BCE) are the oldest substantial
religious texts in Egyptian. This module provides phonemic decoding
using the wheel verb system.

Bidirectional reading:
- Forward (L→R): Ascending, cohering, unifying — becoming
- Reverse (R→L): Descending, decohering, dissolving — undoing
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .corpus import Sentence, load_tla_corpus
from .mapping import WHEEL_VERBS, leiden_to_wheel, phonemes_to_verbs
from .engine import get_hourglass, Mode, Pole


# =============================================================================
# READABLE TRANSLATION LAYER
# =============================================================================

# Verb forms for natural prose: verb → (gerund, noun, third_person, imperative)
VERB_FORMS = {
    # Wheel verbs (v63) - masculine equilibrium
    'integrate': ('integrating', 'wholeness', 'integrates', 'integrate'),
    'radiate': ('radiating', 'radiance', 'radiates', 'radiate'),
    'emerge': ('emerging', 'emergence', 'emerges', 'emerge'),
    'direct': ('directing', 'direction', 'directs', 'direct'),
    'lead': ('leading', 'the path', 'leads', 'lead'),
    'read': ('reading', 'meaning', 'reads', 'read'),
    'express': ('expressing', 'expression', 'expresses', 'express'),
    'shine': ('shining', 'light', 'shines', 'shine'),
    'true': ('truing', 'truth', 'trues', 'true'),
    'honour': ('honouring', 'honour', 'honours', 'honour'),
    'devote': ('devoting', 'devotion', 'devotes', 'devote'),
    'receive': ('receiving', 'receiving', 'receives', 'receive'),
    'store': ('storing', 'the treasury', 'stores', 'store'),
    'bestow': ('bestowing', 'the gift', 'bestows', 'bestow'),
    'embody': ('embodying', 'form', 'embodies', 'embody'),
    'discern': ('discerning', 'clarity', 'discerns', 'discern'),
    # Feminine equilibrium
    'weave': ('weaving', 'the weaving', 'weaves', 'weave'),
    'flow': ('flowing', 'flow', 'flows', 'flow'),
    'cocoon': ('cocooning', 'stillness', 'cocoons', 'cocoon'),
    'align': ('aligning', 'alignment', 'aligns', 'align'),
    'tend': ('tending', 'care', 'tends', 'tend'),
    'etch': ('etching', 'inscription', 'etches', 'etch'),
    'interpret': ('interpreting', 'understanding', 'interprets', 'interpret'),
    'bask': ('basking', 'warmth', 'basks', 'bask'),
    'trust': ('trusting', 'trust', 'trusts', 'trust'),
    'allow': ('allowing', 'openness', 'allows', 'allow'),
    'restore': ('restoring', 'renewal', 'restores', 'restore'),
    'cultivate': ('cultivating', 'growth', 'cultivates', 'cultivate'),
    'gather': ('gathering', 'abundance', 'gathers', 'gather'),
    'protect': ('protecting', 'sanctuary', 'protects', 'protect'),
    'capacity': ('holding', 'capacity', 'holds', 'hold'),
    'act': ('acting', 'action', 'acts', 'act'),
    # Spine verbs
    'cycle': ('cycling', 'the turning', 'cycles', 'turn'),
    'do': ('doing', 'deed', 'does', 'do'),
    'fundament': ('grounding', 'foundation', 'grounds', 'ground'),
    'ground': ('grounding', 'earth', 'grounds', 'ground'),
    'breathe': ('breathing', 'breath', 'breathes', 'breathe'),
    'see': ('seeing', 'vision', 'sees', 'see'),
}


def _gerund(verb: str) -> str:
    """Convert verb to gerund form."""
    v = verb.lower()
    # Check if already a compound phrase
    if ' upon ' in v or ' and ' in v:
        return v
    if v in VERB_FORMS:
        return VERB_FORMS[v][0]
    if v.endswith('e'):
        return v[:-1] + 'ing'
    return v + 'ing'


def _noun(verb: str) -> str:
    """Convert verb to noun form."""
    v = verb.lower()
    # Check if already a compound phrase
    if ' upon ' in v or ' and ' in v:
        return v
    if v in VERB_FORMS:
        return VERB_FORMS[v][1]
    return v


def _third(verb: str) -> str:
    """Convert verb to third person form."""
    v = verb.lower()
    # Check if already a compound phrase
    if ' upon ' in v or ' and ' in v:
        return 'deepens'
    if v in VERB_FORMS:
        return VERB_FORMS[v][2]
    if v.endswith('s') or v.endswith('sh') or v.endswith('ch'):
        return v + 'es'
    return v + 's'


def _imperative(verb: str) -> str:
    """Convert verb to imperative form."""
    v = verb.lower()
    # Check if already a compound phrase
    if ' upon ' in v or ' and ' in v:
        return v
    if v in VERB_FORMS:
        return VERB_FORMS[v][3]
    return v


def translate_to_readable(verbs: List[str], direction: str = "ascend") -> str:
    """
    Translate verb sequence into flowing readable English.
    
    Uses varied sentence structures for natural, poetic prose.
    """
    if not verbs:
        return ""
    
    sentences = []
    i = 0
    pattern_idx = 0
    
    # Ascending patterns: building, rising, becoming
    ascend_patterns = [
        # 5-verb patterns
        lambda v: f"From {_noun(v[0])}, {_noun(v[1])} rises into {_noun(v[2])}—{_gerund(v[3])}, {_gerund(v[4])}.",
        lambda v: f"{_noun(v[0]).capitalize()} opens to {_noun(v[1])}. {_noun(v[2]).capitalize()} meets {_noun(v[3])}, and {_noun(v[4])} dawns.",
        lambda v: f"As {_noun(v[0])} {_third(v[1])}, {_noun(v[2])} {_third(v[3])} toward {_noun(v[4])}.",
        lambda v: f"Here: {_noun(v[0])}, {_noun(v[1])}, {_noun(v[2])}. Then {_noun(v[3])} becoming {_noun(v[4])}.",
        lambda v: f"{_imperative(v[0]).capitalize()}, {_imperative(v[1])}, {_imperative(v[2])}—until {_noun(v[3])} {_third(v[4])}.",
    ]
    
    # Descending patterns: returning, dissolving, surrendering  
    descend_patterns = [
        lambda v: f"{_noun(v[0]).capitalize()} returns through {_noun(v[1])} into {_noun(v[2])}—{_gerund(v[3])}, {_gerund(v[4])}.",
        lambda v: f"Down from {_noun(v[0])}: {_noun(v[1])} folds into {_noun(v[2])}, {_noun(v[3])} dissolves to {_noun(v[4])}.",
        lambda v: f"As {_noun(v[0])} releases, {_noun(v[1])} {_third(v[2])} back toward {_noun(v[3])}, finding {_noun(v[4])}.",
        lambda v: f"{_noun(v[0]).capitalize()} surrenders to {_noun(v[1])}. {_noun(v[2]).capitalize()} meets {_noun(v[3])}, returning to {_noun(v[4])}.",
        lambda v: f"Release {_noun(v[0])}, release {_noun(v[1])}—{_noun(v[2])} {_third(v[3])} home to {_noun(v[4])}.",
    ]
    
    # 4-verb patterns
    four_patterns_asc = [
        lambda v: f"{_noun(v[0]).capitalize()} and {_noun(v[1])} entwine; {_noun(v[2])} {_third(v[3])}.",
        lambda v: f"Through {_gerund(v[0])}, {_noun(v[1])} finds {_noun(v[2])}. {_noun(v[3]).capitalize()} follows.",
        lambda v: f"{_gerund(v[0]).capitalize()} into {_gerund(v[1])}—{_noun(v[2])} reveals {_noun(v[3])}.",
    ]
    
    four_patterns_desc = [
        lambda v: f"{_noun(v[0]).capitalize()} unwinds to {_noun(v[1])}; {_noun(v[2])} returns to {_noun(v[3])}.",
        lambda v: f"Releasing {_noun(v[0])}, {_noun(v[1])} softens to {_noun(v[2])}, then {_noun(v[3])}.",
        lambda v: f"From {_noun(v[0])} back through {_noun(v[1])}—{_noun(v[2])} finds {_noun(v[3])}.",
    ]
    
    # 3-verb patterns
    three_patterns_asc = [
        lambda v: f"{_noun(v[0]).capitalize()}, {_noun(v[1])}, {_noun(v[2])}.",
        lambda v: f"In {_noun(v[0])}: {_noun(v[1])} and {_noun(v[2])}.",
        lambda v: f"{_gerund(v[0]).capitalize()}, {_gerund(v[1])}, {_gerund(v[2])}.",
    ]
    
    three_patterns_desc = [
        lambda v: f"{_noun(v[0]).capitalize()} to {_noun(v[1])} to {_noun(v[2])}.",
        lambda v: f"Back through {_noun(v[0])}, {_noun(v[1])}, {_noun(v[2])}.",
        lambda v: f"{_noun(v[0]).capitalize()} dissolves: {_noun(v[1])}, then {_noun(v[2])}.",
    ]
    
    # 2-verb patterns
    two_patterns_asc = [
        lambda v: f"{_noun(v[0]).capitalize()} becomes {_noun(v[1])}.",
        lambda v: f"From {_noun(v[0])}, {_noun(v[1])}.",
    ]
    
    two_patterns_desc = [
        lambda v: f"{_noun(v[0]).capitalize()} returns to {_noun(v[1])}.",
        lambda v: f"{_noun(v[0]).capitalize()} and {_noun(v[1])}, at rest.",
    ]
    
    # 1-verb patterns
    one_patterns = [
        lambda v: f"{_noun(v[0]).capitalize()}.",
        lambda v: f"And {_noun(v[0])}.",
    ]
    
    is_ascending = direction.lower() in ('ascend', 'ascending', 'forward')
    
    def get_chunk(size):
        """Get chunk, handling immediate repeats gracefully."""
        chunk = verbs[i:i+size]
        result = []
        prev = None
        for v in chunk:
            if v.lower() == prev:
                # Immediate repeat - intensify
                n = _noun(v)
                result.append(f"{n} upon {n}")
            else:
                result.append(v)
            prev = v.lower()
        return result
    
    while i < len(verbs):
        remaining = len(verbs) - i
        
        if remaining >= 5:
            chunk = get_chunk(5)
            patterns = ascend_patterns if is_ascending else descend_patterns
            sentence = patterns[pattern_idx % len(patterns)](chunk)
            i += 5
            pattern_idx += 1
            
        elif remaining == 4:
            chunk = get_chunk(4)
            patterns = four_patterns_asc if is_ascending else four_patterns_desc
            sentence = patterns[pattern_idx % len(patterns)](chunk)
            i += 4
            pattern_idx += 1
            
        elif remaining == 3:
            chunk = get_chunk(3)
            patterns = three_patterns_asc if is_ascending else three_patterns_desc
            sentence = patterns[pattern_idx % len(patterns)](chunk)
            i += 3
            pattern_idx += 1
            
        elif remaining == 2:
            chunk = get_chunk(2)
            patterns = two_patterns_asc if is_ascending else two_patterns_desc
            sentence = patterns[pattern_idx % len(patterns)](chunk)
            i += 2
            pattern_idx += 1
            
        else:
            chunk = get_chunk(1)
            sentence = one_patterns[pattern_idx % len(one_patterns)](chunk)
            i += 1
            pattern_idx += 1
        
        sentences.append(sentence)
    
    return '\n'.join(sentences)


# Cache for pyramid texts
_pyramid_texts: List[Sentence] = None


def get_pyramid_texts() -> List[Sentence]:
    """
    Get all Unas Pyramid Text sentences.
    
    These are dated -2375 to -2345 BCE, the reign of Unas,
    whose pyramid contains the oldest Pyramid Texts.
    
    Returns:
        List of Sentence objects in corpus order
    """
    global _pyramid_texts
    
    if _pyramid_texts is not None:
        return _pyramid_texts
    
    corpus = load_tla_corpus()
    
    # Filter for Unas reign specifically
    _pyramid_texts = [
        s for s in corpus
        if s.date_not_before == -2375 and s.date_not_after == -2345
    ]
    
    return _pyramid_texts


@dataclass
class DecodedLine:
    """A decoded line from the Pyramid Texts."""
    index: int
    hieroglyphs: str
    transliteration: str
    translation: str
    phonemes: List[str]
    verbs: List[str]
    trajectory: str


@dataclass
class BidirectionalLine:
    """A line decoded in both directions."""
    index: int
    hieroglyphs: str
    transliteration: str
    phonemes: List[str]
    
    # Forward (L→R): ascending, cohering
    forward_verbs: List[str]
    forward_trajectory: str
    
    # Reverse (R→L): descending, decohering  
    reverse_verbs: List[str]
    reverse_trajectory: str


def decode_bidirectional(
    start: int = 1,
    end: int = 9,
    verbose: bool = True,
    readable: bool = False
) -> Tuple[List[BidirectionalLine], str, str]:
    """
    Decode lines bidirectionally: forward (ascending) and reverse (descending).
    
    Args:
        start: First line (1-based)
        end: Last line (1-based, inclusive)
        verbose: Print results
        readable: Translate to flowing English prose (default False)
        
    Returns:
        Tuple of:
        - List of BidirectionalLine objects
        - Forward paragraph (ascending/cohering)
        - Reverse paragraph (descending/decohering)
    """
    texts = get_pyramid_texts()
    
    # Convert to 0-based
    start_idx = start - 1
    end_idx = end  # end is inclusive, so end_idx = end for range()
    
    if start_idx >= len(texts):
        raise ValueError(f"Start line {start} exceeds corpus size {len(texts)}")
    
    end_idx = min(end_idx, len(texts))
    
    results = []
    all_forward_verbs = []
    all_reverse_verbs = []
    
    for i in range(start_idx, end_idx):
        s = texts[i]
        
        # Forward (L→R)
        forward_verbs = s.verbs
        forward_trajectory = ' → '.join(forward_verbs)
        
        # Reverse (R→L)
        reverse_verbs = list(reversed(s.verbs))
        reverse_trajectory = ' → '.join(reverse_verbs)
        
        decoded = BidirectionalLine(
            index=i,
            hieroglyphs=s.hieroglyphs,
            transliteration=s.transliteration,
            phonemes=s.phonemes,
            forward_verbs=forward_verbs,
            forward_trajectory=forward_trajectory,
            reverse_verbs=reverse_verbs,
            reverse_trajectory=reverse_trajectory,
        )
        results.append(decoded)
        all_forward_verbs.extend(forward_verbs)
        all_reverse_verbs.extend(reverse_verbs)
    
    # Build paragraphs
    if readable:
        forward_paragraph = translate_to_readable(all_forward_verbs, "ascend")
        reverse_paragraph = translate_to_readable(all_reverse_verbs, "descend")
    else:
        forward_paragraph = build_paragraph(all_forward_verbs, "ascending")
        reverse_paragraph = build_paragraph(all_reverse_verbs, "descending")
    
    if verbose:
        print_bidirectional(results, forward_paragraph, reverse_paragraph, start, end_idx)
    
    return results, forward_paragraph, reverse_paragraph


def build_paragraph(verbs: List[str], mode: str) -> str:
    """
    Build flowing prose from verb sequence.
    
    Each clause becomes a sentence on its own line.
    Verbs are woven with natural connectives.
    """
    if not verbs:
        return ""
    
    # Group into clauses (chunks of ~5-7 verbs for rhythm)
    clause_size = 6
    sentences = []
    
    for i in range(0, len(verbs), clause_size):
        chunk = verbs[i:i+clause_size]
        sentence = weave_clause(chunk)
        sentences.append(sentence)
    
    # Each sentence on its own line
    return '\n'.join(sentences)


def weave_clause(verbs: List[str]) -> str:
    """
    Weave a list of verbs into a prose sentence.
    
    Adds natural connectives and flow.
    """
    if not verbs:
        return ""
    
    if len(verbs) == 1:
        return verbs[0].capitalize() + "."
    
    # Build sentence with natural rhythm
    # Pattern: VERB, VERB and VERB; VERB to VERB, VERB.
    parts = []
    i = 0
    while i < len(verbs):
        v = verbs[i].lower()
        
        # Decide connective based on position
        if i == 0:
            parts.append(v.capitalize())
        elif i == len(verbs) - 1:
            # Last verb - use "and" or "to"
            prev = verbs[i-1].lower()
            if prev in ['bind', 'weave', 'form', 'protect']:
                parts.append(f"to {v}")
            else:
                parts.append(f"and {v}")
        elif i % 3 == 0:
            # Every third, use semicolon for breath
            parts.append(f"; {v}")
        elif verbs[i-1].lower() == verbs[i].lower():
            # Repeated verb - emphasize
            parts.append(f"and {v}")
        else:
            # Normal flow
            parts.append(v)
        
        i += 1
    
    # Join with spaces, end with period
    text = ' '.join(parts)
    # Clean up spacing around semicolons
    text = text.replace(' ; ', '; ')
    return text + "."


def print_bidirectional(
    results: List[BidirectionalLine],
    forward_para: str,
    reverse_para: str,
    start: int,
    end: int
):
    """Pretty-print bidirectional decode results."""
    
    print(f"\n{'='*70}")
    print(f"BIDIRECTIONAL DECODE: Lines {start}-{end}")
    print(f"{'='*70}")
    
    # Line-by-line
    for line in results:
        print(f"\n--- Line {line.index + 1} ({len(line.phonemes)} phonemes) ---")
        print(f"𓀀 {line.hieroglyphs[:60]}{'...' if len(line.hieroglyphs) > 60 else ''}")
        print(f"◯ {line.transliteration[:60]}{'...' if len(line.transliteration) > 60 else ''}")
        print(f"\n↗ ASCEND:  {line.forward_trajectory}")
        print(f"↙ DESCEND: {line.reverse_trajectory}")
    
    # Aggregate paragraphs
    print(f"\n{'='*70}")
    print("ASCENDING (Forward L→R)")
    print("Cohere • Unify • Become • Build")
    print(f"{'='*70}")
    print(f"\n{forward_para}")
    
    print(f"\n{'='*70}")
    print("DESCENDING (Reverse R→L)")
    print("Decohere • Dissolve • Undo • Return")
    print(f"{'='*70}")
    print(f"\n{reverse_para}")
    
    # Summary statistics
    total_phonemes = sum(len(line.phonemes) for line in results)
    print(f"\n{'='*70}")
    print(f"STATISTICS")
    print(f"{'='*70}")
    print(f"Lines: {len(results)}")
    print(f"Total phonemes: {total_phonemes}")
    print(f"Phonemes per line: {[len(line.phonemes) for line in results]}")
    
    # Check for Fibonacci 1+2+3+2+1=9 structure
    if len(results) == 9:
        fib_struct = [1, 2, 3, 2, 1]
        print(f"\n9-line Fibonacci breath: {' + '.join(map(str, fib_struct))} = 9")


def decode(n: int, start: int = 0, verbose: bool = True) -> List[DecodedLine]:
    """
    Decode N lines from the Pyramid Texts starting at index `start`.
    
    Args:
        n: Number of lines to decode
        start: Starting index (0-based). Default 0 = first lines.
        verbose: If True, print results as we go
        
    Returns:
        List of DecodedLine objects
    """
    texts = get_pyramid_texts()
    
    if start >= len(texts):
        raise ValueError(f"Start index {start} exceeds corpus size {len(texts)}")
    
    end = min(start + n, len(texts))
    
    results = []
    all_phonemes = []
    all_verbs = []
    
    for i in range(start, end):
        s = texts[i]
        
        decoded = DecodedLine(
            index=i,
            hieroglyphs=s.hieroglyphs,
            transliteration=s.transliteration,
            translation=s.translation,
            phonemes=s.phonemes,
            verbs=s.verbs,
            trajectory=s.trajectory,
        )
        results.append(decoded)
        all_phonemes.extend(s.phonemes)
        all_verbs.extend(s.verbs)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"LINE {i+1}")
            print(f"{'='*60}")
            print(f"𓀀 {s.hieroglyphs}")
            print(f"◯ {s.transliteration}")
            print(f"→ {s.translation}")
            print(f"\nPHONEMES: {' '.join(s.phonemes)}")
            print(f"VERBS: {s.trajectory}")
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"AGGREGATE: Lines {start+1}-{end}")
        print(f"{'='*60}")
        print(f"Total phonemes: {len(all_phonemes)}")
        print(f"\nCOMBINED STREAM:")
        # Show in chunks of 20
        for i in range(0, len(all_verbs), 10):
            chunk = all_verbs[i:i+10]
            print(f"  {i+1:3}-{i+len(chunk):3}: {' → '.join(chunk)}")
        
        # Frequency analysis
        from collections import Counter
        freq = Counter(all_phonemes)
        print(f"\nFREQUENCY (n={len(all_phonemes)}):")
        for p, count in freq.most_common():
            pct = 100 * count / len(all_phonemes)
            verb = WHEEL_VERBS.get(p, '?')
            print(f"  {p:3} ({verb:10}): {count:3} ({pct:5.1f}%)")
    
    return results


def decode_range(start: int, end: int, verbose: bool = True) -> List[DecodedLine]:
    """
    Decode lines from start to end (inclusive).
    
    Args:
        start: First line (1-based for human readability)
        end: Last line (1-based, inclusive)
        verbose: Print results
        
    Returns:
        List of DecodedLine objects
    """
    # Convert to 0-based
    return decode(end - start + 1, start - 1, verbose)


if __name__ == '__main__':
    # Decode first 9 lines bidirectionally (Fibonacci breath block)
    decode_bidirectional(1, 9)


# =============================================================================
# LAYERED DECODE: Five simultaneous readings
# =============================================================================

@dataclass
class LayeredReading:
    """Five parallel readings of a phoneme sequence."""
    phonemes: List[str]
    core: List[str]      # All equilibrium
    f1: List[str]        # min_fem alternating with eq
    f2: List[str]        # max_fem alternating with eq
    m1: List[str]        # min_masc alternating with eq
    m2: List[str]        # max_masc alternating with eq


def get_layered_verb(phoneme: str, position: int, mode: Mode, pole: Pole) -> str:
    """
    Get verb for a phoneme at a position in a specific layer.
    
    Pattern: (pole)(eq)(pole)(eq)(pole)...
    - Odd positions (0, 2, 4...): use the specified pole
    - Even positions (1, 3, 5...): use equilibrium
    """
    hg = get_hourglass(phoneme)
    if not hg:
        return f'?{phoneme}'
    
    # Alternating: position 0, 2, 4... = pole; position 1, 3, 5... = eq
    use_pole = (position % 2 == 0)
    
    if not use_pole:
        # Equilibrium position - use core verb based on mode
        return hg.equilibrium_masc if mode == Mode.MASCULINE else hg.equilibrium_fem
    
    # Pole position
    if mode == Mode.MASCULINE:
        return hg.min_masc if pole == Pole.MINIMA else hg.max_masc
    else:
        return hg.min_fem if pole == Pole.MINIMA else hg.max_fem


def decode_layered_sequence(phonemes: List[str]) -> LayeredReading:
    """
    Decode a phoneme sequence into five parallel layers.
    
    Layers:
    - core: all equilibrium (masculine by convention)
    - f1: min_fem at odd positions, eq at even
    - f2: max_fem at odd positions, eq at even
    - m1: min_masc at odd positions, eq at even
    - m2: max_masc at odd positions, eq at even
    """
    core = []
    f1, f2 = [], []
    m1, m2 = [], []
    
    for i, p in enumerate(phonemes):
        hg = get_hourglass(p)
        if not hg:
            verb = f'?{p}'
            core.append(verb)
            f1.append(verb)
            f2.append(verb)
            m1.append(verb)
            m2.append(verb)
            continue
        
        # Core is always equilibrium
        core.append(hg.equilibrium_masc)
        
        # Layered: alternating pole/eq
        f1.append(get_layered_verb(p, i, Mode.FEMININE, Pole.MINIMA))
        f2.append(get_layered_verb(p, i, Mode.FEMININE, Pole.MAXIMA))
        m1.append(get_layered_verb(p, i, Mode.MASCULINE, Pole.MINIMA))
        m2.append(get_layered_verb(p, i, Mode.MASCULINE, Pole.MAXIMA))
    
    return LayeredReading(
        phonemes=phonemes,
        core=core,
        f1=f1, f2=f2,
        m1=m1, m2=m2,
    )


def decode_layered(
    start: int = 1,
    end: int = 9,
    verbose: bool = True
) -> Tuple[LayeredReading, LayeredReading]:
    """
    Decode lines with five parallel layers, in both directions.
    
    ASCEND (L→R): core, then F layers, then M layers
    PENETRATE (R→L): core, then M layers, then F layers
    
    Args:
        start: First line (1-based)
        end: Last line (1-based, inclusive)
        verbose: Print results
        
    Returns:
        Tuple of (ascend_reading, penetrate_reading)
    """
    texts = get_pyramid_texts()
    
    start_idx = start - 1
    end_idx = min(end, len(texts))
    
    # Collect all phonemes
    all_phonemes = []
    for i in range(start_idx, end_idx):
        s = texts[i]
        phonemes = leiden_to_wheel(s.transliteration)
        all_phonemes.extend(phonemes)
    
    # Decode forward (ASCEND)
    ascend = decode_layered_sequence(all_phonemes)
    
    # Decode reverse (PENETRATE)
    penetrate = decode_layered_sequence(list(reversed(all_phonemes)))
    
    if verbose:
        print_layered(ascend, penetrate, start, end_idx)
    
    return ascend, penetrate


def print_layered(ascend: LayeredReading, penetrate: LayeredReading, start: int, end: int):
    """Pretty-print layered decode results."""
    
    print(f"\n{'═' * 70}")
    print(f"LAYERED DECODE: Lines {start}-{end}")
    print(f"{'═' * 70}")
    print(f"Total phonemes: {len(ascend.phonemes)}")
    
    # ASCEND: core, F, M
    print(f"\n{'─' * 70}")
    print("ASCEND (L→R)")
    print("F leads up: core → f1 → f2 → m1 → m2")
    print(f"{'─' * 70}")
    
    print("\n[CORE]")
    print(build_paragraph(ascend.core, "ascend"))
    
    print("\n[F1 - min_fem]")
    print(build_paragraph(ascend.f1, "ascend"))
    
    print("\n[F2 - max_fem]")
    print(build_paragraph(ascend.f2, "ascend"))
    
    print("\n[M1 - min_masc]")
    print(build_paragraph(ascend.m1, "ascend"))
    
    print("\n[M2 - max_masc]")
    print(build_paragraph(ascend.m2, "ascend"))
    
    # PENETRATE: core, M, F
    print(f"\n{'─' * 70}")
    print("PENETRATE (R→L)")
    print("M leads down: core → m1 → m2 → f1 → f2")
    print(f"{'─' * 70}")
    
    print("\n[CORE]")
    print(build_paragraph(penetrate.core, "penetrate"))
    
    print("\n[M1 - min_masc]")
    print(build_paragraph(penetrate.m1, "penetrate"))
    
    print("\n[M2 - max_masc]")
    print(build_paragraph(penetrate.m2, "penetrate"))
    
    print("\n[F1 - min_fem]")
    print(build_paragraph(penetrate.f1, "penetrate"))
    
    print("\n[F2 - max_fem]")
    print(build_paragraph(penetrate.f2, "penetrate"))


# Pyramid translations cache
_pyramid_translations: list = None


def load_pyramid_translations() -> list:
    """
    Load pre-computed Pyramid Text translations.
    
    Returns list of dicts, each containing:
        - id: sequential number (1-based)
        - transliteration: original Leiden transliteration
        - phonemes: list of wheel/spine phonemes
        - verbs: list of verb names
        - trajectory: condensed verb path (first 10)
        - ascend: prose translation (L→R, rising)
        - penetrate: prose translation (R→L, entering)
        - period: "Old Kingdom" etc.
        - date_range: e.g., "-2345 to -2315 BCE"
    
    Example:
        >>> corpus = load_pyramid_translations()
        >>> print(corpus[0]['ascend'])
        'Emerge bestow shine; radiate integrate and bestow...'
    """
    global _pyramid_translations
    
    if _pyramid_translations is not None:
        return _pyramid_translations
    
    import json
    from pathlib import Path
    
    path = Path(__file__).parent / 'data' / 'pyramid_texts_translated.json'
    with open(path, 'r', encoding='utf-8') as f:
        _pyramid_translations = json.load(f)
    
    return _pyramid_translations


def translate(transliteration: str, direction: str = "ascend") -> str:
    """
    Translate Egyptian transliteration to readable English prose.
    
    Args:
        transliteration: Leiden transliteration (e.g., "ꜥnḫ wḏꜣ snb")
        direction: "ascend" (L→R, rising) or "penetrate" (R→L, entering)
    
    Returns:
        Flowing English prose interpretation
    
    Example:
        >>> from eye_of_horus import translate
        >>> translate("(w)sꞽr wnꞽs ꞽbꜣ")
        'Emerge bestow shine; radiate integrate and bestow.\nEmerge bestow receive and lead.'
        
        >>> translate("ꜥnḫ wḏꜣ snb", direction="penetrate")
        'Receive integrate emerge; radiate discern and lead.\nHonour and integrate.'
    """
    from .mapping import leiden_to_wheel, phonemes_to_verbs
    
    phonemes = leiden_to_wheel(transliteration)
    
    if direction == "penetrate":
        phonemes = list(reversed(phonemes))
    
    verbs = phonemes_to_verbs(phonemes)
    return build_paragraph(verbs, direction)


def translate_bidirectional(transliteration: str) -> dict:
    """
    Translate in both directions simultaneously.
    
    Args:
        transliteration: Leiden transliteration
    
    Returns:
        Dict with 'ascend', 'penetrate', 'phonemes', 'verbs'
    
    Example:
        >>> result = translate_bidirectional("ꜥnḫ wḏꜣ snb")
        >>> print(result['ascend'])
        >>> print(result['penetrate'])
    """
    from .mapping import leiden_to_wheel, phonemes_to_verbs
    
    phonemes = leiden_to_wheel(transliteration)
    verbs = phonemes_to_verbs(phonemes)
    
    return {
        'phonemes': phonemes,
        'verbs': verbs,
        'trajectory': ' → '.join(verbs),
        'ascend': build_paragraph(verbs, "ascend"),
        'penetrate': build_paragraph(list(reversed(verbs)), "penetrate"),
    }
