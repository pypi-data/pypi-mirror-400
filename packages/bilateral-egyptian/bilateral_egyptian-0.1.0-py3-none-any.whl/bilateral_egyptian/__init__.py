"""
Bilateral Egyptian Analysis Toolkit

A Python package for analyzing bilateral semantic structure in Egyptian hieroglyphics.
Based on the bilateral covenant hypothesis (Brown, 2026).

This package provides tools for:
- Detecting mirror pairs (phonetically reversible word pairs)
- Analyzing bilateral compounds
- Calculating Mirror-Axis Ratio (MAR)
- Identifying medial ayin positioning
- Stratification analysis across historical periods

References:
    Brown, N.D. (2026). The Bilateral Covenant: Mirror Symmetry as Semantic Structure 
    in Egyptian Hieroglyphics. DOI: 10.5281/zenodo.18168786
"""

__version__ = "0.1.0"
__author__ = "Nicholas David Brown"
__email__ = "research@bilateral-egyptian.org"

from .analysis import (
    calculate_mar,
    analyze_ayin_position,
    bilateral_reading,
)

from .mirror_pairs import (
    detect_mirror_pair,
    find_mirror_pairs,
    KNOWN_MIRROR_PAIRS,
)

from .compounds import (
    analyze_compound,
    extract_proto_phonemes,
    assess_covenant_status,
    PROTO_PHONEMES,
)

from .stratification import (
    stratify_by_period,
    calculate_period_mar,
    compare_relational_vocabulary,
)

__all__ = [
    # Core analysis
    "calculate_mar",
    "analyze_ayin_position", 
    "bilateral_reading",
    # Mirror pairs
    "detect_mirror_pair",
    "find_mirror_pairs",
    "KNOWN_MIRROR_PAIRS",
    # Compounds
    "analyze_compound",
    "extract_proto_phonemes",
    "assess_covenant_status",
    "PROTO_PHONEMES",
    # Stratification
    "stratify_by_period",
    "calculate_period_mar",
    "compare_relational_vocabulary",
]
