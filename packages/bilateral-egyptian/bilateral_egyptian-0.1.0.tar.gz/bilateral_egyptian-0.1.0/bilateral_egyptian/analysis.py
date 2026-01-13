"""
Core analysis functions for bilateral Egyptian analysis.

This module provides the fundamental analytical tools for detecting
and measuring bilateral semantic structure in Egyptian hieroglyphic texts.
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter


def calculate_mar(words: List[str], bilateral_words: List[str]) -> float:
    """
    Calculate Mirror-Axis Ratio (MAR) for a vocabulary set.
    
    MAR measures the proportion of vocabulary exhibiting bilateral structure.
    Higher MAR indicates stronger preservation of bilateral encoding.
    
    Args:
        words: List of all words in the corpus
        bilateral_words: List of words identified as having bilateral structure
        
    Returns:
        Float between 0.0 and 1.0 representing the MAR
        
    Example:
        >>> words = ["maat", "ka", "ba", "nfr", "simple"]
        >>> bilateral = ["maat", "ka", "ba", "nfr"]
        >>> calculate_mar(words, bilateral)
        0.8
    """
    if not words:
        return 0.0
    
    bilateral_set = set(bilateral_words)
    count = sum(1 for w in words if w in bilateral_set)
    return count / len(words)


def analyze_ayin_position(word: str, ayin_char: str = "ꜥ") -> Dict[str, any]:
    """
    Analyze the position of ayin in a word.
    
    The bilateral hypothesis predicts medial ayin positioning at ~67.5%
    versus ~34% expected from random distribution.
    
    Args:
        word: The transliterated Egyptian word
        ayin_char: Character representing ayin (default: ꜥ)
        
    Returns:
        Dictionary containing:
            - has_ayin: bool
            - position: int (0-indexed) or None
            - is_medial: bool
            - relative_position: float (0.0-1.0, where 0.5 is center)
            
    Example:
        >>> analyze_ayin_position("mꜥꜣt")
        {'has_ayin': True, 'position': 1, 'is_medial': True, 'relative_position': 0.25}
    """
    if ayin_char not in word:
        return {
            "has_ayin": False,
            "position": None,
            "is_medial": False,
            "relative_position": None
        }
    
    position = word.index(ayin_char)
    word_len = len(word)
    relative = position / (word_len - 1) if word_len > 1 else 0.5
    
    # Medial = not first or last position
    is_medial = 0 < position < word_len - 1
    
    return {
        "has_ayin": True,
        "position": position,
        "is_medial": is_medial,
        "relative_position": round(relative, 3)
    }


def bilateral_reading(word: str, reverse: bool = False) -> str:
    """
    Generate bilateral reading of a word.
    
    Returns the word read in specified direction. Use with
    proto-phoneme analysis for full bilateral interpretation.
    
    Args:
        word: The transliterated Egyptian word
        reverse: If True, return reversed reading
        
    Returns:
        The word in specified reading direction
        
    Example:
        >>> bilateral_reading("nfr")
        'nfr'
        >>> bilateral_reading("nfr", reverse=True)
        'rfn'
    """
    if reverse:
        return word[::-1]
    return word


def detect_bilateral_structure(word: str, known_bilateral: Optional[List[str]] = None) -> Dict:
    """
    Detect whether a word exhibits bilateral structure.
    
    Checks for:
    - Presence in known bilateral vocabulary
    - Palindromic structure
    - Medial ayin positioning
    - Proto-phoneme composition
    
    Args:
        word: The transliterated Egyptian word
        known_bilateral: Optional list of known bilateral words
        
    Returns:
        Dictionary with detection results and confidence score
    """
    from .compounds import extract_proto_phonemes, PROTO_PHONEMES
    
    results = {
        "word": word,
        "is_bilateral": False,
        "confidence": 0.0,
        "indicators": []
    }
    
    # Check known bilateral vocabulary
    if known_bilateral and word in known_bilateral:
        results["indicators"].append("known_bilateral")
        results["confidence"] += 0.4
    
    # Check palindromic
    if word == word[::-1]:
        results["indicators"].append("palindromic")
        results["confidence"] += 0.2
    
    # Check ayin positioning
    ayin_analysis = analyze_ayin_position(word)
    if ayin_analysis["is_medial"]:
        results["indicators"].append("medial_ayin")
        results["confidence"] += 0.3
    
    # Check proto-phoneme composition
    proto_phonemes = extract_proto_phonemes(word)
    if proto_phonemes:
        results["indicators"].append("proto_phoneme_present")
        results["confidence"] += 0.1 * len(proto_phonemes)
    
    results["confidence"] = min(1.0, results["confidence"])
    results["is_bilateral"] = results["confidence"] >= 0.3
    
    return results


def batch_analyze(words: List[str]) -> Dict:
    """
    Perform batch analysis on a word list.
    
    Returns aggregate statistics including:
    - Total word count
    - Bilateral word count and percentage
    - Medial ayin frequency
    - Proto-phoneme distribution
    
    Args:
        words: List of transliterated Egyptian words
        
    Returns:
        Dictionary with aggregate analysis results
    """
    results = {
        "total_words": len(words),
        "bilateral_count": 0,
        "medial_ayin_count": 0,
        "ayin_words": 0,
        "proto_phoneme_counts": Counter()
    }
    
    from .compounds import extract_proto_phonemes
    
    for word in words:
        # Bilateral detection
        detection = detect_bilateral_structure(word)
        if detection["is_bilateral"]:
            results["bilateral_count"] += 1
        
        # Ayin analysis
        ayin = analyze_ayin_position(word)
        if ayin["has_ayin"]:
            results["ayin_words"] += 1
            if ayin["is_medial"]:
                results["medial_ayin_count"] += 1
        
        # Proto-phoneme extraction
        protos = extract_proto_phonemes(word)
        results["proto_phoneme_counts"].update(protos)
    
    # Calculate derived metrics
    results["mar"] = results["bilateral_count"] / results["total_words"] if words else 0
    results["medial_ayin_ratio"] = (
        results["medial_ayin_count"] / results["ayin_words"] 
        if results["ayin_words"] else 0
    )
    
    return results
