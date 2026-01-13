"""
Bilateral compound analysis.

This module provides tools for analyzing compound words according
to the bilateral covenant framework, including proto-phoneme extraction
and covenant status assessment.

The eleven proto-phonemes are: BA, DA, HA, KA, LA, MA, NA, RA, SHA, TA, WA
These center on ayin (ꜥ) as the covenant axis.
"""

from typing import List, Dict, Optional, Tuple
import re


# The eleven proto-phonemes (bilateral roots)
PROTO_PHONEMES = {
    "BA": {
        "phoneme": "b",
        "meaning": "soul-container",
        "examples": ["bꜣ (soul)", "ꜣb (heart)"],
        "bilateral_pair": ("bꜣ", "ꜣb")
    },
    "DA": {
        "phoneme": "d",
        "meaning": "hand/give",
        "examples": ["di (give)", "id (boy)"],
        "bilateral_pair": ("di", "id")
    },
    "HA": {
        "phoneme": "h",
        "meaning": "breath/descend",
        "examples": ["hꜣ (descend)", "ꜣh (spirit)"],
        "bilateral_pair": ("hꜣ", "ꜣh")
    },
    "KA": {
        "phoneme": "k",
        "meaning": "vital force",
        "examples": ["kꜣ (soul)", "ꜣk (luminous)"],
        "bilateral_pair": ("kꜣ", "ꜣk")
    },
    "LA": {
        "phoneme": "l",
        "meaning": "tongue/extension",  # Note: rare in Egyptian, often → r
        "examples": [],
        "bilateral_pair": None
    },
    "MA": {
        "phoneme": "m",
        "meaning": "water/mother",
        "examples": ["mw (water)", "mwt (mother)"],
        "bilateral_pair": ("mw", "wm")
    },
    "NA": {
        "phoneme": "n",
        "meaning": "negation/toward",
        "examples": ["n (to/for)", "nn (these)"],
        "bilateral_pair": ("nw", "wn")
    },
    "RA": {
        "phoneme": "r",
        "meaning": "mouth/sun",
        "examples": ["rꜥ (sun/Ra)", "ꜥr (rise)"],
        "bilateral_pair": ("rꜥ", "ꜥr")
    },
    "SHA": {
        "phoneme": "š",
        "meaning": "pool/garden",
        "examples": ["šw (Shu)", "wš (empty)"],
        "bilateral_pair": ("šw", "wš")
    },
    "TA": {
        "phoneme": "t",
        "meaning": "bread/earth",
        "examples": ["tꜣ (land)", "ꜣt (moment)"],
        "bilateral_pair": ("tꜣ", "ꜣt")
    },
    "WA": {
        "phoneme": "w",
        "meaning": "one/uniqueness",
        "examples": ["wꜥ (one)", "ꜥw (extent)"],
        "bilateral_pair": ("wꜥ", "ꜥw")
    },
}

# Covenant status categories
COVENANT_STATUS = {
    "intact": "Bilateral structure preserved, reciprocal meaning accessible",
    "externalized": "Covenant axis projected outward, relational meaning",
    "collapsed": "Bilateral structure degraded, unilateral reading only",
    "contaminated": "Mixed bilateral/non-bilateral elements"
}


def extract_proto_phonemes(word: str) -> List[str]:
    """
    Extract proto-phonemes present in a word.
    
    Identifies which of the eleven proto-phonemes are present
    in the given word.
    
    Args:
        word: The transliterated Egyptian word
        
    Returns:
        List of proto-phoneme names found in the word
        
    Example:
        >>> extract_proto_phonemes("bꜣ")
        ['BA']
        >>> extract_proto_phonemes("kꜣmwt")
        ['KA', 'MA', 'TA']
    """
    found = []
    word_lower = word.lower()
    
    for name, info in PROTO_PHONEMES.items():
        phoneme = info["phoneme"]
        if phoneme in word_lower:
            found.append(name)
    
    return found


def analyze_compound(word: str, meaning: Optional[str] = None) -> Dict:
    """
    Perform full bilateral analysis on a compound word.
    
    Analyzes:
    - Proto-phoneme composition
    - Forward and reverse readings
    - Covenant status
    - Bilateral coherence
    
    Args:
        word: The transliterated Egyptian word
        meaning: Optional known meaning for enhanced analysis
        
    Returns:
        Dictionary with complete analysis
        
    Example:
        >>> analyze_compound("ꜥnḫ", "life")
        {
            'word': 'ꜥnḫ',
            'meaning': 'life',
            'forward': 'ꜥnḫ',
            'reverse': 'ḫnꜥ',
            'proto_phonemes': ['NA', 'KA'],
            'has_ayin': True,
            'ayin_medial': True,
            'covenant_status': 'intact',
            'bilateral_reading': 'reaching through transformation ↔ transformation with'
        }
    """
    from .analysis import analyze_ayin_position
    
    forward = word
    reverse = word[::-1]
    
    proto_phonemes = extract_proto_phonemes(word)
    ayin_analysis = analyze_ayin_position(word)
    
    # Determine covenant status
    if ayin_analysis["is_medial"]:
        covenant_status = "intact"
    elif ayin_analysis["has_ayin"]:
        covenant_status = "externalized"
    elif proto_phonemes:
        covenant_status = "collapsed"
    else:
        covenant_status = "contaminated"
    
    result = {
        "word": word,
        "meaning": meaning,
        "forward": forward,
        "reverse": reverse,
        "proto_phonemes": proto_phonemes,
        "has_ayin": ayin_analysis["has_ayin"],
        "ayin_medial": ayin_analysis["is_medial"],
        "ayin_position": ayin_analysis["relative_position"],
        "covenant_status": covenant_status,
        "covenant_description": COVENANT_STATUS.get(covenant_status, "Unknown")
    }
    
    return result


def assess_covenant_status(word: str) -> Tuple[str, str]:
    """
    Assess the covenant status of a word.
    
    Categories:
    - intact: Bilateral structure preserved
    - externalized: Covenant axis projected outward
    - collapsed: Bilateral structure degraded
    - contaminated: Mixed elements
    
    Args:
        word: The transliterated Egyptian word
        
    Returns:
        Tuple of (status_code, description)
        
    Example:
        >>> assess_covenant_status("mꜥꜣt")
        ('intact', 'Bilateral structure preserved, reciprocal meaning accessible')
    """
    from .analysis import analyze_ayin_position
    
    ayin = analyze_ayin_position(word)
    protos = extract_proto_phonemes(word)
    
    if ayin["is_medial"]:
        return ("intact", COVENANT_STATUS["intact"])
    elif ayin["has_ayin"]:
        return ("externalized", COVENANT_STATUS["externalized"])
    elif protos:
        return ("collapsed", COVENANT_STATUS["collapsed"])
    else:
        return ("contaminated", COVENANT_STATUS["contaminated"])


def generate_bilateral_gloss(word: str, forward_gloss: str, reverse_gloss: str) -> str:
    """
    Generate a bilateral gloss combining forward and reverse readings.
    
    Args:
        word: The transliterated Egyptian word
        forward_gloss: Meaning of forward reading
        reverse_gloss: Meaning of reverse reading
        
    Returns:
        Combined bilateral gloss string
        
    Example:
        >>> generate_bilateral_gloss("ꜥnḫ", "arm-toward-sieve", "sieve-from-arm")
        'arm-toward-sieve ↔ sieve-from-arm'
    """
    return f"{forward_gloss} ↔ {reverse_gloss}"


def batch_compound_analysis(words: List[str]) -> Dict:
    """
    Analyze multiple compounds and return aggregate statistics.
    
    Args:
        words: List of transliterated Egyptian words
        
    Returns:
        Dictionary with aggregate analysis including:
        - covenant_status_distribution
        - proto_phoneme_frequency
        - bilateral_coherence_rate
    """
    from collections import Counter
    
    status_counts = Counter()
    proto_counts = Counter()
    bilateral_count = 0
    
    for word in words:
        analysis = analyze_compound(word)
        status_counts[analysis["covenant_status"]] += 1
        proto_counts.update(analysis["proto_phonemes"])
        
        if analysis["covenant_status"] in ("intact", "externalized"):
            bilateral_count += 1
    
    return {
        "total_words": len(words),
        "covenant_status_distribution": dict(status_counts),
        "proto_phoneme_frequency": dict(proto_counts),
        "bilateral_count": bilateral_count,
        "bilateral_coherence_rate": bilateral_count / len(words) if words else 0
    }
