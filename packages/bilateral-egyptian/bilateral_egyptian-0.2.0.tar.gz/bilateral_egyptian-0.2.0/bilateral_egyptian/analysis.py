"""
Core analysis functions for bilateral Egyptian analysis.
"""

from typing import List, Dict, Optional
from collections import Counter


def calculate_mar(words: List[str], bilateral_words: List[str]) -> float:
    """Calculate Mirror-Axis Ratio (MAR) for a vocabulary set."""
    if not words:
        return 0.0
    bilateral_set = set(bilateral_words)
    count = sum(1 for w in words if w in bilateral_set)
    return count / len(words)


def analyze_ayin_position(word: str, ayin_char: str = "ꜥ") -> Dict:
    """Analyze the position of ayin in a word."""
    if ayin_char not in word:
        return {"has_ayin": False, "position": None, "is_medial": False, "relative_position": None}
    
    position = word.index(ayin_char)
    word_len = len(word)
    relative = position / (word_len - 1) if word_len > 1 else 0.5
    is_medial = 0 < position < word_len - 1
    
    return {"has_ayin": True, "position": position, "is_medial": is_medial, "relative_position": round(relative, 3)}


def bilateral_reading(word: str, reverse: bool = False) -> str:
    """Generate bilateral reading of a word."""
    return word[::-1] if reverse else word
