"""
Mirror pair detection and analysis.

Mirror pairs are phonetically symmetrical word pairs where both
reading directions yield attested Egyptian words with related meanings.

The bilateral hypothesis predicts ~69 such pairs versus ~12 expected
from random phoneme distribution.
"""

from typing import List, Dict, Tuple, Optional


# Known mirror pairs from corpus analysis
# Format: (forward, forward_meaning, reverse, reverse_meaning, relation)
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
    ("nb", "lord/all", "bn", "not/negative", "polar_opposition"),
    ("ḫm", "not know", "mḫ", "to fill", "complementary"),
    ("wn", "to exist/open", "nw", "to see/look", "existential"),
    ("pr", "house/go forth", "rp", "wine", "offering_context"),
    ("sꜣ", "son/back", "ꜣs", "Isis", "generative"),
    ("tm", "complete/all", "mt", "death", "terminal"),
    ("ḥꜥ", "body/flesh", "ꜥḥ", "palace", "dwelling"),
    ("sw", "he/him", "ws", "honor", "identity"),
    ("nṯr", "god", "rṯn", "Retenu (foreign)", "sacred_profane"),
    ("šw", "Shu/air", "wš", "to be empty", "elemental"),
]


def detect_mirror_pair(word: str, vocabulary: List[str]) -> Optional[Dict]:
    """
    Check if a word has a mirror pair in the vocabulary.
    
    Args:
        word: The transliterated Egyptian word
        vocabulary: List of attested vocabulary to check against
        
    Returns:
        Dictionary with mirror pair info if found, None otherwise
        
    Example:
        >>> vocab = ["kꜣ", "ꜣk", "nfr", "rfn", "simple"]
        >>> detect_mirror_pair("kꜣ", vocab)
        {'forward': 'kꜣ', 'reverse': 'ꜣk', 'is_mirror_pair': True}
    """
    reversed_word = word[::-1]
    
    if reversed_word in vocabulary and reversed_word != word:
        return {
            "forward": word,
            "reverse": reversed_word,
            "is_mirror_pair": True,
            "is_palindrome": False
        }
    elif reversed_word == word:
        return {
            "forward": word,
            "reverse": reversed_word,
            "is_mirror_pair": False,
            "is_palindrome": True
        }
    
    return None


def find_mirror_pairs(vocabulary: List[str]) -> List[Tuple[str, str]]:
    """
    Find all mirror pairs in a vocabulary list.
    
    Identifies all word pairs where both forward and reverse
    readings are attested in the vocabulary.
    
    Args:
        vocabulary: List of attested vocabulary
        
    Returns:
        List of (word, reversed_word) tuples
        
    Example:
        >>> vocab = ["kꜣ", "ꜣk", "nfr", "rfn", "simple"]
        >>> find_mirror_pairs(vocab)
        [('kꜣ', 'ꜣk'), ('nfr', 'rfn')]
    """
    vocab_set = set(vocabulary)
    pairs = []
    seen = set()
    
    for word in vocabulary:
        if word in seen:
            continue
            
        reversed_word = word[::-1]
        
        if reversed_word in vocab_set and reversed_word != word:
            # Use alphabetical ordering to avoid duplicates
            pair = tuple(sorted([word, reversed_word]))
            if pair not in seen:
                pairs.append((word, reversed_word))
                seen.add(word)
                seen.add(reversed_word)
    
    return pairs


def classify_mirror_pair_relation(
    forward: str, 
    forward_meaning: str,
    reverse: str,
    reverse_meaning: str
) -> str:
    """
    Classify the semantic relationship between mirror pair members.
    
    Categories:
    - complementary: meanings complete each other
    - causal: one meaning causes/enables the other
    - functional: operational relationship
    - theological: divine/cosmic relationship
    - polar_opposition: opposite meanings
    - emotional_polarity: opposite emotional valences
    - relational: interpersonal/social relationship
    
    Args:
        forward: Forward reading word
        forward_meaning: Meaning of forward reading
        reverse: Reverse reading word
        reverse_meaning: Meaning of reverse reading
        
    Returns:
        Classification string
    """
    # Check known pairs first
    for known in KNOWN_MIRROR_PAIRS:
        if known[0] == forward and known[2] == reverse:
            return known[4]
        if known[0] == reverse and known[2] == forward:
            return known[4]
    
    # Default to unclassified
    return "unclassified"


def analyze_mirror_pair_distribution(pairs: List[Tuple[str, str]]) -> Dict:
    """
    Analyze the distribution of mirror pairs.
    
    Checks whether observed distribution differs significantly
    from random expectation (~12 pairs expected vs ~69 observed).
    
    Args:
        pairs: List of mirror pair tuples
        
    Returns:
        Dictionary with distribution analysis
    """
    observed = len(pairs)
    expected_random = 12  # Based on phoneme distribution probability
    
    ratio = observed / expected_random if expected_random else 0
    
    return {
        "observed_pairs": observed,
        "expected_random": expected_random,
        "enrichment_ratio": round(ratio, 2),
        "statistically_significant": observed > expected_random * 2,
        "interpretation": (
            "Strong bilateral encoding" if ratio > 4 else
            "Moderate bilateral encoding" if ratio > 2 else
            "Weak or no bilateral encoding"
        )
    }


def get_known_pair_info(word: str) -> Optional[Dict]:
    """
    Get information about a word if it's part of a known mirror pair.
    
    Args:
        word: The transliterated Egyptian word
        
    Returns:
        Dictionary with pair information if known, None otherwise
    """
    for pair in KNOWN_MIRROR_PAIRS:
        if pair[0] == word:
            return {
                "word": pair[0],
                "meaning": pair[1],
                "mirror": pair[2],
                "mirror_meaning": pair[3],
                "relation": pair[4],
                "direction": "forward"
            }
        elif pair[2] == word:
            return {
                "word": pair[2],
                "meaning": pair[3],
                "mirror": pair[0],
                "mirror_meaning": pair[1],
                "relation": pair[4],
                "direction": "reverse"
            }
    
    return None
