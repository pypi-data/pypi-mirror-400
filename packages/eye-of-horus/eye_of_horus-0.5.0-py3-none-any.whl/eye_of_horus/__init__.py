# Eye of Horus - Egyptian Phonemic Analysis
# For reading ancient Egyptian through the 16-position wheel
#
# Engine: 16 wheel phonemes × 3 spine axes = 408 grammar (T(16) × 3)

__version__ = "0.5.0"

# Core mapping (Leiden → wheel phonemes)
from .mapping import (
    leiden_to_wheel,
    WHEEL_16,
    LEIDEN_TO_WHEEL,
    WHEEL_VERBS,
    phonemes_to_verbs,
)

# Hourglass engine (full semantic architecture)
from .engine import (
    # Enums
    Mode,
    Pole,
    Scale,
    SpinePhoneme,
    # Data structures
    Hourglass,
    Relation,
    TriangularRelation,
    # Phoneme data
    PHONEME_HOURGLASSES,
    PHONEME_ORDER,
    WHEEL_PHONEMES,
    SPINE_PRIMARY,
    SPINE_SECONDARY,
    SPINE_ALL,
    # Functions
    get_hourglass,
    get_core_verb,
    triangular,
    generate_relations,
    count_relations,
    get_all_relations,
    total_grammar,
    generate_all_triangular_relations,
    get_all_triangular_relations,
    count_triangular_relations,
    detect_mode,
    decode_with_mode,
    decode_trajectory,
    is_wheel_phoneme,
    is_spine_phoneme,
    classify_phoneme,
)

# Corpus access
from .corpus import (
    load_tla_corpus,
    search_corpus,
    Sentence,
    load_semantic_network,
    get_edge_signature,
    find_edges_by_signature,
)

# Validation tools
from .validation import (
    oldest_sentences,
    test_oldest_sentences,
    test_causal_coherence,
    DirectionTest,
    find_markers,
    show_sentence_detail,
)

# Pyramid Texts
from .pyramid import (
    get_pyramid_texts,
    load_pyramid_translations,
    translate,
    translate_bidirectional,
    decode,
    decode_range,
    decode_bidirectional,
    decode_layered,
    DecodedLine,
    BidirectionalLine,
    LayeredReading,
)

# Fibonacci Rhythm & Breath
from .rhythm import (
    PHI,
    PHI_INV,
    FIBONACCI,
    BreathPhase,
    ScriptHealth,
    fibonacci,
    detect_phi_boundaries,
    detect_yuga_boundaries,
    detect_breath_phase,
    score_script_health,
    get_fibonacci_line_structure,
    is_at_phi_boundary,
    segment_by_fibonacci,
    analyze_line_rhythm,
    SCRIPT_RATIOS,
)

# Bitwise engine (fast vectorized decode)
from .bitwise import (
    # IDs
    PHONEME_TO_ID,
    ID_TO_PHONEME,
    NUM_PHONEMES,
    NUM_WHEEL,
    NUM_SPINE,
    # Position encoding
    Pos,
    Layer,
    LAYER_POS,
    # Tables
    VERB_TABLE,
    CORE_VERB_TABLE,
    # Encoding
    encode_phonemes,
    decode_ids,
    semantic_address,
    address_to_components,
    # Classification (bitwise)
    is_wheel as is_wheel_fast,
    is_spine as is_spine_fast,
    is_wheel_array,
    is_spine_array,
    # Layered decode
    decode_layer,
    decode_all_layers,
    decode_layered as decode_layered_fast,
    LayeredResult,
    decode_text,
    # Relations
    relation_index,
    relation_to_pair,
    NUM_WHEEL_RELATIONS,
    # Grammar
    grammar_index,
    grammar_to_components,
    TOTAL_GRAMMAR,
    # Convenience
    phonemes_to_verbs_fast,
)
