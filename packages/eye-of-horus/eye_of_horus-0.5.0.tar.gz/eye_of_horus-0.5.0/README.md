# Eye of Horus

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18196732.svg)](https://doi.org/10.5281/zenodo.18196732)
[![PyPI version](https://badge.fury.io/py/eye-of-horus.svg)](https://pypi.org/project/eye-of-horus/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

A phonemic engine for reading ancient Egyptian through the 16-position wheel.

## The 408 Grammar

```
T(16) = 136 wheel relations × 3 spine axes = 408
```

Sixteen phonemes on a vorticular wheel. Three scales on a spine. Trigonal decode across three modes. Every Egyptian utterance decoded through directed semantic relations.

## Installation

```bash
pip install eye-of-horus
```

## Quick Start

```python
from eye_of_horus import load_pyramid_translations

# 1,316 Pyramid Text sentences, pre-translated
corpus = load_pyramid_translations()

for entry in corpus[:3]:
    print(entry['transliteration'])
    print(entry['ascend'])      # Rising (L→R)
    print(entry['penetrate'])   # Entering (R→L)
    print()
```

## The Wheel (16 phonemes)

Each phoneme maps 1:1 to a deity, with masculine and feminine equilibrium verbs representing antithetic poles of the same semantic axis:

| Pos | Ph | Deity | F equilibrium | M equilibrium |
|-----|-----|-------|---------------|---------------|
| 1 | n | Neith | WEAVE | INTEGRATE |
| 2 | w | Wadjet | FLOW | RADIATE |
| 3 | s | Sekhmet | CRYSTALLISE | EMERGE |
| 4 | sh | Shu | ALIGN | DIRECT |
| 5 | A | Atum | TEND | LEAD |
| 6 | t | Seshat | ETCH | READ |
| 7 | H | Horus | INTERPRET | EXPRESS |
| 8 | r | Ra | BASK | SHINE |
| 9 | m | Ma'at | TRUST | TRUE |
| 10 | a | Anubis | ALLOW | HONOUR |
| 11 | y | Isis | RESTORE | DEVOTE |
| 12 | b | Bes | CULTIVATE | RECEIVE |
| 13 | p | Ptah | GATHER | STORE |
| 14 | i | Ihy | PROTECT | BESTOW |
| 15 | kh | Khnum | CAPACITY | EMBODY |
| 16 | dj | Thoth | ACT | DISCERN |

## The Spine (3 scales)

Spine phonemes operate across temporal scales, outside the wheel:

| Phoneme | Verb | Scale |
|---------|------|-------|
| k | CYCLE | Ontogenic (individual lifecycle) |
| d | DO | Phylogenic (species/lineage) |
| x | FUNDAMENT | Cosmogenic (universal) |

Secondary spine: g (GROUND), f (BREATHE), h (SEE).

**Critical:** Plain d and k are spine. The wheel has dj (palatalized), not plain d.

## The Pyramidal Architecture (5 positions)

Each phoneme occupies five positions in a pyramidal structure (two pyramids apex-to-apex):

```
          max_masc
             △
            /|\
           / | \
          / min_m \
         /___△___\
              |
        eq_m ─┼─ eq_f
              |
         \___▽___/
          \ max_f /
           \ | /
            \|/
             ▽
          min_fem
```

## Trigonal Decode

The three modes (equilibrium, feminine, masculine) generate five parallel interpretations:

| Layer | Mode | Pole | Pattern |
|-------|------|------|---------|
| core | — | equilibrium | all eq |
| f1 | feminine | min_fem | (pole)(eq)(pole)(eq)... |
| f2 | feminine | max_fem | (pole)(eq)(pole)(eq)... |
| m1 | masculine | min_masc | (pole)(eq)(pole)(eq)... |
| m2 | masculine | max_masc | (pole)(eq)(pole)(eq)... |

The alternation creates rhythmic pulsing: reach to pole, return to center.

## Bidirectional Reading

Direction determines layer order:

| Direction | Movement | Layer Order |
|-----------|----------|-------------|
| **ASCEND** (L→R) | Rising, feminine leads | core → f1 → f2 → m1 → m2 |
| **PENETRATE** (R→L) | Entering, masculine leads | core → m1 → m2 → f1 → f2 |

```python
from eye_of_horus import decode_bidirectional

results, ascend, penetrate = decode_bidirectional(1, 9, readable=True)
print(ascend)
```

## Total Decode Space

```
3 modes (5 outputs) × 2 directions = 10 simultaneous readings
408 relations × 5 positions = 2,040 meaning-positions
```

## Directed Pairs

The 136 wheel edges capture Egyptian vocabulary semantics:

```python
from eye_of_horus import get_edge_signature

edge = get_edge_signature('a', 'n')  # ankh
print(edge['signatures']['life']['ratio'])  # 11.08x baseline
```

| Edge | Verbs | Semantic field | Egyptian |
|------|-------|----------------|----------|
| p→t | STORE→READ | sky 13x | pt |
| a→n | HONOUR→INTEGRATE | life 11x | ankh |
| m→w | TRUE→RADIATE | water 10x | mw |
| dj→m | DISCERN→TRUE | speech 8x | djed-medu |

## Fibonacci Breath

The Pyramid Texts' opening follows a 1+2+3+2+1 = 9 structure:

```
        1         ← Line 1: SEED
       / \
      2   2       ← Lines 2-3: Division
     / \ / \
    3   3   3     ← Lines 4-5-6: Peak
     \ / \ /
      2   2       ← Lines 7-8: Return
       \ /
        1         ← Line 9: Unity
```

The hourglass rotated 90°—same architecture at text level.

## Semantic Network

240 directed edges validated against 12,773 TLA sentences:

```python
from eye_of_horus import find_edges_by_signature

# Find all edges associated with "life" (>5x baseline)
for edge in find_edges_by_signature('life', 5.0):
    print(f"{edge['edge']} {edge['verbs']} — {edge['ratio']}x")
```

## Performance

Full corpus decode in 18ms on MacBook Air M4 (14µs per sentence).

## Corpus

| Dataset | Sentences | Source |
|---------|-----------|--------|
| Pyramid Texts | 1,316 | Old Kingdom walls (~2300 BCE) |
| Semantic Network | 240 edges | Derived from TLA corpus |

## API Reference

```python
from eye_of_horus import (
    # Mapping
    leiden_to_wheel,
    phonemes_to_verbs,
    WHEEL_16,
    WHEEL_VERBS,
    
    # Pyramid Texts
    load_pyramid_translations,
    decode_bidirectional,
    decode_layered,
    
    # Semantic Network
    load_semantic_network,
    get_edge_signature,
    find_edges_by_signature,
    
    # Engine
    Mode, Pole, Scale,
    get_hourglass,
    triangular,
    total_grammar,
)
```

## License

MIT

## Citation

If you use this in academic work:

```bibtex
@software{brown_2025_eye_of_horus,
  author       = {Brown, Nicholas David},
  title        = {{Eye of Horus: A Phonemic Analysis Engine for Ancient Egyptian Texts}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18196732},
  url          = {https://doi.org/10.5281/zenodo.18196732}
}
```

## Author

Nicholas David Brown  
Independent Researcher

---

*The wheel rotates. The spine holds. The layers speak simultaneously.*
