"""Mirror pair detection and analysis."""

from typing import List, Dict, Tuple, Optional

KNOWN_MIRROR_PAIRS = [
    ("kꜣ", "soul/spirit", "ꜣk", "luminous spirit", "complementary"),
    ("bꜣ", "soul", "ꜣb", "heart", "complementary"),
    ("nfr", "good/beautiful", "rfn", "to rejoice", "causal"),
    ("wꜣs", "power/dominion", "sꜣw", "to guard", "functional"),
    ("ḥtp", "peace/offering", "ptḥ", "Ptah (creator)", "theological"),
    ("mn", "to remain/endure", "nm", "to guide/lead", "complementary"),
    ("ꜥnḫ", "life", "ḫnꜥ", "together with", "relational"),
    ("sn", "brother", "ns", "tongue/speech", "functional"),
    ("mr", "love", "rm", "to weep", "emotional_polarity"),
    ("ḥr", "face/upon", "rḥ", "to know", "perceptual"),
]


def detect_mirror_pair(word: str, vocabulary: List[str]) -> Optional[Dict]:
    """Check if a word has a mirror pair in the vocabulary."""
    reversed_word = word[::-1]
    if reversed_word in vocabulary and reversed_word != word:
        return {"forward": word, "reverse": reversed_word, "is_mirror_pair": True, "is_palindrome": False}
    elif reversed_word == word:
        return {"forward": word, "reverse": reversed_word, "is_mirror_pair": False, "is_palindrome": True}
    return None


def find_mirror_pairs(vocabulary: List[str]) -> List[Tuple[str, str]]:
    """Find all mirror pairs in a vocabulary list."""
    vocab_set = set(vocabulary)
    pairs = []
    seen = set()
    
    for word in vocabulary:
        if word in seen:
            continue
        reversed_word = word[::-1]
        if reversed_word in vocab_set and reversed_word != word:
            pair = tuple(sorted([word, reversed_word]))
            if pair not in seen:
                pairs.append((word, reversed_word))
                seen.add(word)
                seen.add(reversed_word)
    return pairs
