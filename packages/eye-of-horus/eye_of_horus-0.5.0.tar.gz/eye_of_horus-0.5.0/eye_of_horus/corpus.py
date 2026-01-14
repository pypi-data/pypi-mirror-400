"""
TLA corpus loading and search utilities.

Provides access to 12,773 Earlier Egyptian sentences from the
Thesaurus Linguae Aegyptiae database.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Iterator
from dataclasses import dataclass

from .mapping import leiden_to_wheel, phonemes_to_verbs


@dataclass
class Sentence:
    """A single Egyptian sentence with all metadata."""
    hieroglyphs: str
    transliteration: str
    lemmatization: str
    upos: str
    glossing: str
    translation: str
    date_not_before: int
    date_not_after: int
    
    # Computed fields
    phonemes: List[str] = None
    verbs: List[str] = None
    
    def __post_init__(self):
        """Compute phoneme and verb sequences."""
        self.phonemes = leiden_to_wheel(self.transliteration)
        self.verbs = phonemes_to_verbs(self.phonemes)
    
    @property
    def trajectory(self) -> str:
        """Human-readable verb trajectory."""
        return ' → '.join(self.verbs)
    
    @property
    def date_range(self) -> str:
        """Formatted date range."""
        return f"{self.date_not_before} to {self.date_not_after} BCE"
    
    @property
    def period(self) -> str:
        """Historical period classification."""
        if self.date_not_before <= -2686:
            return "Early Dynastic"
        elif self.date_not_before <= -2181:
            return "Old Kingdom"
        elif self.date_not_before <= -2055:
            return "First Intermediate"
        elif self.date_not_before <= -1650:
            return "Middle Kingdom"
        else:
            return "Late"


# Module-level corpus cache
_corpus: List[Sentence] = None
_corpus_path: Path = None


def load_tla_corpus(path: Optional[str] = None) -> List[Sentence]:
    """
    Load the TLA Earlier Egyptian corpus.
    
    Args:
        path: Path to JSON file. If None, uses default location.
    
    Returns:
        List of Sentence objects
    """
    global _corpus, _corpus_path
    
    if path is None:
        # Default: look in package data directory
        path = Path(__file__).parent / 'data' / 'tla_earlier_egyptian.json'
    else:
        path = Path(path)
    
    # Return cached if same path
    if _corpus is not None and _corpus_path == path:
        return _corpus
    
    sentences = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            sent = Sentence(
                hieroglyphs=row['hieroglyphs'],
                transliteration=row['transliteration'],
                lemmatization=row['lemmatization'],
                upos=row['UPOS'],
                glossing=row['glossing'],
                translation=row['translation'],
                date_not_before=int(row['dateNotBefore']) if row['dateNotBefore'] else -3000,
                date_not_after=int(row['dateNotAfter']) if row['dateNotAfter'] else -1500,
            )
            sentences.append(sent)
    
    _corpus = sentences
    _corpus_path = path
    return sentences


def search_corpus(
    query: str = None,
    phoneme_pattern: List[str] = None,
    period: str = None,
    limit: int = 20
) -> Iterator[Sentence]:
    """
    Search the corpus with various filters.
    
    Args:
        query: Text to search in transliteration or translation
        phoneme_pattern: List of phonemes to match at start
        period: "Old Kingdom", "Middle Kingdom", etc.
        limit: Maximum results to return
    
    Yields:
        Matching Sentence objects
    """
    corpus = load_tla_corpus()
    count = 0
    
    for sent in corpus:
        if count >= limit:
            break
            
        # Text query
        if query:
            q = query.lower()
            if q not in sent.transliteration.lower() and q not in sent.translation.lower():
                continue
        
        # Phoneme pattern match
        if phoneme_pattern:
            if sent.phonemes[:len(phoneme_pattern)] != phoneme_pattern:
                continue
        
        # Period filter
        if period:
            if sent.period != period:
                continue
        
        yield sent
        count += 1


def find_by_verb_sequence(verbs: List[str], limit: int = 10) -> Iterator[Sentence]:
    """
    Find sentences whose trajectory starts with given verbs.
    
    Args:
        verbs: List of verb names (e.g., ['FORM', 'MEASURE'])
        limit: Maximum results
    
    Yields:
        Matching sentences
    """
    corpus = load_tla_corpus()
    count = 0
    
    for sent in corpus:
        if count >= limit:
            break
        if sent.verbs[:len(verbs)] == verbs:
            yield sent
            count += 1


# Semantic network data
_semantic_network: dict = None


def load_semantic_network() -> dict:
    """
    Load the pre-computed semantic network of directed edges.
    
    Returns dict with:
        - metadata: corpus stats, baseline frequencies
        - nodes: 16 wheel phonemes with verbs
        - edges: 240 directed pairs with semantic signatures
    
    Each edge has:
        - source, target: phonemes
        - source_verb, target_verb: verb names
        - count: occurrences in corpus
        - signatures: dict of semantic field → {count, ratio, observed_pct}
        - top_signatures: [(field, ratio), ...] top 3 by ratio
        - examples: sample sentences
    """
    global _semantic_network
    
    if _semantic_network is not None:
        return _semantic_network
    
    path = Path(__file__).parent / 'data' / 'semantic_network.json'
    with open(path, 'r', encoding='utf-8') as f:
        _semantic_network = json.load(f)
    
    return _semantic_network


def get_edge_signature(source: str, target: str) -> dict:
    """
    Get semantic signature for a directed edge.
    
    Args:
        source: source phoneme (e.g., 'a')
        target: target phoneme (e.g., 'n')
    
    Returns:
        Edge data with signatures, or None if not found
    """
    network = load_semantic_network()
    for edge in network['edges']:
        if edge['source'] == source and edge['target'] == target:
            return edge
    return None


def find_edges_by_signature(field: str, min_ratio: float = 2.0) -> list:
    """
    Find all edges strongly associated with a semantic field.
    
    Args:
        field: semantic field (divine, death, life, eye, speech, 
               offering, protection, water, sky, earth, king, magic)
        min_ratio: minimum ratio vs baseline (default 2.0 = 2x expected)
    
    Returns:
        List of edges sorted by ratio descending
    """
    network = load_semantic_network()
    results = []
    
    for edge in network['edges']:
        if field in edge['signatures']:
            sig = edge['signatures'][field]
            if sig['ratio'] >= min_ratio:
                results.append({
                    'edge': f"{edge['source']}→{edge['target']}",
                    'verbs': f"{edge['source_verb']}→{edge['target_verb']}",
                    'ratio': sig['ratio'],
                    'count': edge['count']
                })
    
    results.sort(key=lambda x: -x['ratio'])
    return results
