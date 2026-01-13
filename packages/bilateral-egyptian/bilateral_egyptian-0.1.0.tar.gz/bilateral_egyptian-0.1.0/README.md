# Bilateral Egyptian

A Python toolkit for analyzing bilateral semantic structure in Egyptian hieroglyphics.

Based on the bilateral covenant hypothesis (Brown, 2026), which proposes that mirror symmetry in Egyptian hieroglyphic composition encodes semantic structure rather than aesthetic preference.

## Installation

```bash
pip install bilateral-egyptian
```

## Quick Start

```python
from bilateral_egyptian import (
    analyze_compound,
    detect_mirror_pair,
    calculate_mar,
    KNOWN_MIRROR_PAIRS
)

# Analyze a compound word
result = analyze_compound("mꜥꜣt")
print(result)
# {'word': 'mꜥꜣt', 'covenant_status': 'intact', 'ayin_medial': True, ...}

# Check for mirror pairs
vocab = ["kꜣ", "ꜣk", "bꜣ", "ꜣb", "nfr"]
pair = detect_mirror_pair("kꜣ", vocab)
print(pair)
# {'forward': 'kꜣ', 'reverse': 'ꜣk', 'is_mirror_pair': True}

# Calculate Mirror-Axis Ratio
words = ["mꜥꜣt", "kꜣ", "bꜣ", "simple", "other"]
bilateral = ["mꜥꜣt", "kꜣ", "bꜣ"]
mar = calculate_mar(words, bilateral)
print(f"MAR: {mar}")  # MAR: 0.6
```

## Features

### Mirror Pair Detection
Identifies phonetically symmetrical word pairs where both reading directions yield attested Egyptian words with related meanings.

```python
from bilateral_egyptian import find_mirror_pairs, KNOWN_MIRROR_PAIRS

# Find all mirror pairs in a vocabulary
pairs = find_mirror_pairs(vocabulary_list)

# Access known mirror pairs with semantic analysis
for pair in KNOWN_MIRROR_PAIRS[:5]:
    print(f"{pair[0]} ({pair[1]}) ↔ {pair[2]} ({pair[3]}): {pair[4]}")
```

### Bilateral Compound Analysis
Analyzes compound words for proto-phoneme composition, ayin positioning, and covenant status.

```python
from bilateral_egyptian import analyze_compound, extract_proto_phonemes

# Full bilateral analysis
result = analyze_compound("ꜥnḫ", meaning="life")

# Extract proto-phonemes
protos = extract_proto_phonemes("kꜣmwt")
print(protos)  # ['KA', 'MA', 'TA']
```

### Stratification Analysis
Analyzes bilateral structure across historical periods, testing the degradation hypothesis.

```python
from bilateral_egyptian import calculate_period_mar, EgyptianPeriod

result = calculate_period_mar(
    words=old_kingdom_words,
    bilateral_words=old_kingdom_bilateral,
    period=EgyptianPeriod.OLD_KINGDOM
)
print(result)
# {'period': 'old_kingdom', 'observed_mar': 0.72, 'baseline_mar': 0.72, ...}
```

## The Bilateral Covenant Hypothesis

This toolkit implements analytical methods from the bilateral covenant hypothesis, which proposes:

1. **Mirror Symmetry as Structure**: Egyptian hieroglyphic art and architecture encodes semantic structure through bilateral symmetry, not merely aesthetic preference.

2. **Eleven Proto-Phonemes**: The Egyptian phonemic system reduces to eleven bilateral roots (BA, DA, HA, KA, LA, MA, NA, RA, SHA, TA, WA) centering on ayin (ꜥ) as covenant axis.

3. **Declining MAR**: Mirror-Axis Ratio declines from Old Kingdom (0.72) through Late Period (0.54), consistent with transmission degradation.

4. **Relational Preservation**: Relational vocabulary (kinship, reciprocal actions, covenant formulas) maintains elevated MAR (+9.2%) across all periods.

## References

- Brown, N.D. (2026a). The Bilateral Covenant: Mirror Symmetry as Semantic Structure in Egyptian Hieroglyphics. [DOI: 10.5281/zenodo.18168786](https://doi.org/10.5281/zenodo.18168786)

- Brown, N.D. (2026b). Bilateral Egyptian Dictionary: Methodology and Core Entries. [DOI: 10.5281/zenodo.18169109](https://doi.org/10.5281/zenodo.18169109)

- Brown, N.D. (2026c). Bilateral Inscription Architecture: Spatial Predictions from Phonemic-Semantic Analysis. (Forthcoming)

## License

MIT License

## Contributing

Contributions welcome. Please read the contributing guidelines and submit pull requests to the GitHub repository.

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{bilateral_egyptian,
  author = {Brown, Nicholas David},
  title = {Bilateral Egyptian: Tools for Analyzing Bilateral Semantic Structure},
  year = {2026},
  url = {https://github.com/bilateral-egyptian/bilateral-egyptian}
}
```
