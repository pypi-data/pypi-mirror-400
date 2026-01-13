"""
Packed Bit-Width Anagram Hashing for Egyptian Hieroglyphic Analysis.

Adapts the PBWAH algorithm (Brown, 2026; DOI: 10.5281/zenodo.18168195) for
accelerated mirror pair detection and bilateral structure analysis in
Egyptian hieroglyphic corpora.

Key optimizations:
- O(1) anagram comparison via packed bit hashing
- O(n) corpus-wide mirror pair detection
- Near-anagram queries for degraded bilateral vocabulary
- Proto-phoneme fingerprinting for bilateral clustering
"""

from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict


# Egyptian consonant inventory (~30 phonemes)
# Transliteration scheme follows standard Egyptological convention
EGYPTIAN_PHONEMES = [
    'ꜣ',  # aleph
    'ꜥ',  # ayin (covenant axis)
    'w',  # w
    'b',  # b
    'p',  # p
    'f',  # f
    'm',  # m
    'n',  # n
    'r',  # r
    'h',  # h
    'ḥ',  # ḥ (emphatic h)
    'ḫ',  # ḫ (ch)
    'ẖ',  # ẖ (soft ch)
    's',  # s
    'š',  # š (sh)
    'q',  # q
    'k',  # k
    'g',  # g
    't',  # t
    'ṯ',  # ṯ (tj)
    'd',  # d
    'ḏ',  # ḏ (dj)
    'i',  # i/y
    'y',  # y
    'l',  # l (rare, often → r)
]

# Bit-width allocation based on typical Egyptian word frequencies
# Most phonemes need 3-4 bits (max count 7-15 per word)
DEFAULT_BIT_WIDTHS = {phoneme: 4 for phoneme in EGYPTIAN_PHONEMES}
# Common phonemes may need slightly more
DEFAULT_BIT_WIDTHS['n'] = 5  # Very common
DEFAULT_BIT_WIDTHS['r'] = 5
DEFAULT_BIT_WIDTHS['m'] = 5
DEFAULT_BIT_WIDTHS['t'] = 5


class EgyptianPBWAH:
    """
    Packed Bit-Width Anagram Hasher for Egyptian hieroglyphic texts.
    
    Enables O(1) anagram comparison and O(n) mirror pair detection.
    
    Example:
        >>> hasher = EgyptianPBWAH()
        >>> hasher.hash("kꜣ")
        >>> hasher.hash("ꜣk")
        >>> hasher.are_anagrams("kꜣ", "ꜣk")
        True
    """
    
    def __init__(self, bit_widths: Optional[Dict[str, int]] = None):
        """
        Initialize hasher with phoneme bit-width allocation.
        
        Args:
            bit_widths: Optional custom bit-widths per phoneme.
                       Defaults to Egyptian-optimized allocation.
        """
        self.bit_widths = bit_widths or DEFAULT_BIT_WIDTHS.copy()
        self.phonemes = list(self.bit_widths.keys())
        self.phoneme_to_idx = {p: i for i, p in enumerate(self.phonemes)}
        
        # Calculate bit offsets for packing
        self.offsets = {}
        offset = 0
        for phoneme in self.phonemes:
            self.offsets[phoneme] = offset
            offset += self.bit_widths[phoneme]
        
        self.total_bits = offset
        self._cache: Dict[str, int] = {}
    
    def count_phonemes(self, word: str) -> Dict[str, int]:
        """
        Count phoneme frequencies in a word.
        
        Args:
            word: Transliterated Egyptian word
            
        Returns:
            Dictionary of phoneme counts
        """
        counts = defaultdict(int)
        i = 0
        while i < len(word):
            # Check for multi-character phonemes first
            matched = False
            for length in [2, 1]:  # Check 2-char then 1-char
                if i + length <= len(word):
                    substr = word[i:i+length]
                    if substr in self.phoneme_to_idx:
                        counts[substr] += 1
                        i += length
                        matched = True
                        break
            if not matched:
                # Unknown character, skip
                i += 1
        return dict(counts)
    
    def hash(self, word: str) -> int:
        """
        Compute packed bit-width hash for a word.
        
        Args:
            word: Transliterated Egyptian word
            
        Returns:
            Integer hash value (anagram-invariant)
        """
        if word in self._cache:
            return self._cache[word]
        
        counts = self.count_phonemes(word)
        
        packed = 0
        for phoneme, count in counts.items():
            if phoneme in self.offsets:
                offset = self.offsets[phoneme]
                max_val = (1 << self.bit_widths[phoneme]) - 1
                clamped = min(count, max_val)
                packed |= (clamped << offset)
        
        self._cache[word] = packed
        return packed
    
    def are_anagrams(self, word1: str, word2: str) -> bool:
        """
        O(1) anagram comparison after hashing.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if words are anagrams
        """
        return self.hash(word1) == self.hash(word2)
    
    def is_mirror_pair(self, word1: str, word2: str) -> bool:
        """
        Check if two words form a mirror pair.
        
        Mirror pairs are anagrams where one is the reverse of the other.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if word1 reversed equals word2
        """
        # Quick anagram check first (O(1))
        if not self.are_anagrams(word1, word2):
            return False
        # Then verify reversal
        return word1[::-1] == word2
    
    def clear_cache(self):
        """Clear the hash cache."""
        self._cache.clear()


def find_mirror_pairs_fast(
    vocabulary: List[str],
    hasher: Optional[EgyptianPBWAH] = None
) -> List[Tuple[str, str]]:
    """
    Find all mirror pairs in vocabulary using PBWAH acceleration.
    
    Achieves O(n) corpus scanning versus O(n²) naive approach.
    
    Args:
        vocabulary: List of transliterated Egyptian words
        hasher: Optional pre-configured hasher
        
    Returns:
        List of (word, reversed_word) mirror pair tuples
        
    Example:
        >>> vocab = ["kꜣ", "ꜣk", "bꜣ", "ꜣb", "nfr", "rfn", "simple"]
        >>> pairs = find_mirror_pairs_fast(vocab)
        >>> print(pairs)
        [('kꜣ', 'ꜣk'), ('bꜣ', 'ꜣb'), ('nfr', 'rfn')]
    """
    if hasher is None:
        hasher = EgyptianPBWAH()
    
    # Group words by anagram hash - O(n)
    anagram_groups: Dict[int, List[str]] = defaultdict(list)
    vocab_set = set(vocabulary)
    
    for word in vocabulary:
        h = hasher.hash(word)
        anagram_groups[h].append(word)
    
    # Find mirror pairs within each group
    mirror_pairs = []
    seen = set()
    
    for group in anagram_groups.values():
        if len(group) < 2:
            continue
        
        # Check all pairs within group for reversal
        for i, word1 in enumerate(group):
            if word1 in seen:
                continue
            
            reversed_word = word1[::-1]
            
            # Check if reverse exists in vocabulary
            if reversed_word in vocab_set and reversed_word != word1:
                pair = tuple(sorted([word1, reversed_word]))
                if pair not in seen:
                    mirror_pairs.append((word1, reversed_word))
                    seen.add(word1)
                    seen.add(reversed_word)
    
    return mirror_pairs


def group_by_anagram(
    vocabulary: List[str],
    hasher: Optional[EgyptianPBWAH] = None
) -> Dict[int, List[str]]:
    """
    Group vocabulary by anagram equivalence class.
    
    Args:
        vocabulary: List of transliterated Egyptian words
        hasher: Optional pre-configured hasher
        
    Returns:
        Dictionary mapping hash values to word lists
    """
    if hasher is None:
        hasher = EgyptianPBWAH()
    
    groups: Dict[int, List[str]] = defaultdict(list)
    for word in vocabulary:
        h = hasher.hash(word)
        groups[h].append(word)
    
    return dict(groups)


# Proto-phoneme fingerprinting for bilateral clustering
PROTO_PHONEME_BITS = {
    'BA': 0,   # b
    'DA': 1,   # d
    'HA': 2,   # h
    'KA': 3,   # k
    'LA': 4,   # l
    'MA': 5,   # m
    'NA': 6,   # n
    'RA': 7,   # r
    'SHA': 8,  # š
    'TA': 9,   # t
    'WA': 10,  # w
}

PROTO_PHONEME_CHARS = {
    'b': 'BA',
    'd': 'DA',
    'h': 'HA',
    'ḥ': 'HA',
    'k': 'KA',
    'l': 'LA',
    'm': 'MA',
    'n': 'NA',
    'r': 'RA',
    'š': 'SHA',
    't': 'TA',
    'ṯ': 'TA',
    'w': 'WA',
}


def proto_phoneme_fingerprint(word: str) -> int:
    """
    Generate 11-bit proto-phoneme fingerprint.
    
    Each bit indicates presence of corresponding proto-phoneme.
    Enables O(1) bilateral structure similarity comparison.
    
    Args:
        word: Transliterated Egyptian word
        
    Returns:
        11-bit integer fingerprint
        
    Example:
        >>> proto_phoneme_fingerprint("kꜣmwt")  # Contains KA, MA, WA, TA
        0b10001101000  # Bits 3, 5, 9, 10 set
    """
    fingerprint = 0
    
    for char in word:
        if char in PROTO_PHONEME_CHARS:
            proto = PROTO_PHONEME_CHARS[char]
            bit = PROTO_PHONEME_BITS[proto]
            fingerprint |= (1 << bit)
    
    return fingerprint


def bilateral_similarity(word1: str, word2: str) -> float:
    """
    Calculate bilateral structure similarity between words.
    
    Uses proto-phoneme fingerprint Jaccard similarity.
    
    Args:
        word1: First word
        word2: Second word
        
    Returns:
        Similarity score 0.0-1.0
    """
    fp1 = proto_phoneme_fingerprint(word1)
    fp2 = proto_phoneme_fingerprint(word2)
    
    intersection = bin(fp1 & fp2).count('1')
    union = bin(fp1 | fp2).count('1')
    
    if union == 0:
        return 0.0
    
    return intersection / union


def cluster_by_bilateral_structure(
    vocabulary: List[str]
) -> Dict[int, List[str]]:
    """
    Cluster vocabulary by proto-phoneme composition.
    
    Words with identical bilateral structure fingerprints
    are grouped together.
    
    Args:
        vocabulary: List of transliterated Egyptian words
        
    Returns:
        Dictionary mapping fingerprints to word lists
    """
    clusters: Dict[int, List[str]] = defaultdict(list)
    
    for word in vocabulary:
        fp = proto_phoneme_fingerprint(word)
        clusters[fp].append(word)
    
    return dict(clusters)


def find_near_anagrams(
    word: str,
    vocabulary: List[str],
    max_distance: int = 1,
    hasher: Optional[EgyptianPBWAH] = None
) -> List[Tuple[str, int]]:
    """
    Find words that are near-anagrams (differ by few phonemes).
    
    Useful for identifying degraded bilateral vocabulary.
    
    Args:
        word: Target word
        vocabulary: Vocabulary to search
        max_distance: Maximum phoneme count difference
        hasher: Optional pre-configured hasher
        
    Returns:
        List of (word, distance) tuples
    """
    if hasher is None:
        hasher = EgyptianPBWAH()
    
    target_counts = hasher.count_phonemes(word)
    results = []
    
    for candidate in vocabulary:
        if candidate == word:
            continue
        
        cand_counts = hasher.count_phonemes(candidate)
        
        # Calculate edit distance in phoneme-count space
        all_phonemes = set(target_counts.keys()) | set(cand_counts.keys())
        distance = 0
        
        for p in all_phonemes:
            distance += abs(target_counts.get(p, 0) - cand_counts.get(p, 0))
        
        if distance <= max_distance:
            results.append((candidate, distance))
    
    return sorted(results, key=lambda x: x[1])
