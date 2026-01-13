# Bilateral Egyptian

A Python toolkit for analyzing bilateral semantic structure in Egyptian hieroglyphics, with PBWAH-accelerated mirror pair detection.

Based on the bilateral covenant hypothesis (Brown, 2026a) and the Packed Bit-Width Anagram Hashing algorithm (Brown, 2026b).

## Installation

```bash
pip install bilateral-egyptian
```

## Quick Start

```python
from bilateral_egyptian import (
    analyze_compound,
    find_mirror_pairs_fast,
    EgyptianPBWAH,
    proto_phoneme_fingerprint,
)

# Analyze a compound word
result = analyze_compound("mꜥꜣt")
print(result)
# {'word': 'mꜥꜣt', 'covenant_status': 'intact', 'ayin_medial': True, ...}

# Fast mirror pair detection (O(n) vs O(n²))
vocab = ["kꜣ", "ꜣk", "bꜣ", "ꜣb", "nfr", "rfn", "mꜥꜣt"]
pairs = find_mirror_pairs_fast(vocab)
print(pairs)
# [('kꜣ', 'ꜣk'), ('bꜣ', 'ꜣb'), ('nfr', 'rfn')]

# Proto-phoneme fingerprinting
fp = proto_phoneme_fingerprint("kꜣmwt")
print(bin(fp))  # Shows which proto-phonemes present
```

## Features

### PBWAH-Accelerated Analysis (NEW in v0.2.0)

Uses Packed Bit-Width Anagram Hashing for O(1) anagram comparison and O(n) corpus-wide mirror pair detection.

```python
from bilateral_egyptian import EgyptianPBWAH, find_mirror_pairs_fast

# Initialize hasher (Egyptian phoneme-optimized)
hasher = EgyptianPBWAH()

# O(1) anagram check
hasher.are_anagrams("kꜣ", "ꜣk")  # True

# O(1) mirror pair check  
hasher.is_mirror_pair("kꜣ", "ꜣk")  # True

# Find all mirror pairs in large corpus - O(n)
pairs = find_mirror_pairs_fast(large_vocabulary, hasher)
```

### Proto-Phoneme Fingerprinting

11-bit signatures for bilateral structure clustering:

```python
from bilateral_egyptian import (
    proto_phoneme_fingerprint,
    bilateral_similarity,
    cluster_by_bilateral_structure,
)

# Generate fingerprint
fp = proto_phoneme_fingerprint("kꜣmwt")

# Compare bilateral structure similarity
sim = bilateral_similarity("kꜣmwt", "mꜣꜥt")

# Cluster vocabulary by bilateral composition
clusters = cluster_by_bilateral_structure(vocabulary)
```

### Near-Anagram Detection

Find degraded bilateral vocabulary:

```python
from bilateral_egyptian import find_near_anagrams

# Words differing by one phoneme from target
near = find_near_anagrams("kꜣ", vocabulary, max_distance=1)
```

### Mirror Pair Detection

```python
from bilateral_egyptian import find_mirror_pairs, KNOWN_MIRROR_PAIRS

# Standard detection
pairs = find_mirror_pairs(vocabulary_list)

# Access known pairs with semantic analysis
for pair in KNOWN_MIRROR_PAIRS[:5]:
    print(f"{pair[0]} ({pair[1]}) ↔ {pair[2]} ({pair[3]}): {pair[4]}")
```

### Bilateral Compound Analysis

```python
from bilateral_egyptian import analyze_compound, extract_proto_phonemes

# Full bilateral analysis
result = analyze_compound("ꜥnḫ", meaning="life")

# Extract proto-phonemes
protos = extract_proto_phonemes("kꜣmwt")
print(protos)  # ['KA', 'MA', 'TA']
```

### Stratification Analysis

```python
from bilateral_egyptian import calculate_period_mar, EgyptianPeriod

result = calculate_period_mar(
    words=old_kingdom_words,
    bilateral_words=old_kingdom_bilateral,
    period=EgyptianPeriod.OLD_KINGDOM
)
```

## Performance

| Operation | Without PBWAH | With PBWAH |
|-----------|---------------|------------|
| Anagram comparison | O(n) sort or count | O(1) hash compare |
| Find all mirror pairs | O(n²) | O(n) |
| 50,000 word corpus | ~2.5B comparisons | ~50K hashes |

## The Bilateral Covenant Hypothesis

This toolkit implements analytical methods from the bilateral covenant hypothesis:

1. **Mirror Symmetry as Structure**: Egyptian hieroglyphic composition encodes semantic structure through bilateral symmetry.

2. **Eleven Proto-Phonemes**: The phonemic system reduces to eleven bilateral roots centering on ayin (ꜥ) as covenant axis.

3. **Declining MAR**: Mirror-Axis Ratio declines from Old Kingdom (0.72) through Late Period (0.54).

4. **Relational Preservation**: Relational vocabulary maintains elevated MAR (+9.2%) across all periods.

## References

- Brown, N.D. (2026a). The Bilateral Covenant: Mirror Symmetry as Semantic Structure in Egyptian Hieroglyphics. [DOI: 10.5281/zenodo.18168786](https://doi.org/10.5281/zenodo.18168786)

- Brown, N.D. (2026b). Packed Bit-Width Anagram Hashing: A Constant-Time Comparison Algorithm. [DOI: 10.5281/zenodo.18168195](https://doi.org/10.5281/zenodo.18168195)

- Brown, N.D. (2026c). Bilateral Egyptian Dictionary: Methodology and Core Entries. [DOI: 10.5281/zenodo.18169109](https://doi.org/10.5281/zenodo.18169109)

## License

MIT License

## Citation

```bibtex
@software{bilateral_egyptian,
  author = {Brown, Nicholas David},
  title = {Bilateral Egyptian: Tools for Analyzing Bilateral Semantic Structure},
  year = {2026},
  version = {0.2.0},
  url = {https://github.com/bilateral-egyptian/bilateral-egyptian}
}
```
