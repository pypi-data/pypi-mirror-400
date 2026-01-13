"""
Stratification analysis for bilateral Egyptian texts.

This module provides tools for analyzing bilateral structure
across historical periods, testing the hypothesis that MAR
declines over time while relational vocabulary maintains
elevated bilateral structure.

Observed MAR by period:
- Old Kingdom: 0.72
- Middle Kingdom: 0.68
- New Kingdom: 0.60
- Late Period: 0.54
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from enum import Enum


class EgyptianPeriod(Enum):
    """Egyptian historical periods for stratification analysis."""
    OLD_KINGDOM = "old_kingdom"
    MIDDLE_KINGDOM = "middle_kingdom"
    NEW_KINGDOM = "new_kingdom"
    LATE_PERIOD = "late_period"
    PTOLEMAIC = "ptolemaic"
    UNKNOWN = "unknown"


# Expected MAR values by period (from corpus analysis)
PERIOD_MAR_BASELINE = {
    EgyptianPeriod.OLD_KINGDOM: 0.72,
    EgyptianPeriod.MIDDLE_KINGDOM: 0.68,
    EgyptianPeriod.NEW_KINGDOM: 0.60,
    EgyptianPeriod.LATE_PERIOD: 0.54,
    EgyptianPeriod.PTOLEMAIC: 0.48,
}

# Relational vocabulary shows +9.2% MAR above baseline
RELATIONAL_MAR_ELEVATION = 0.092

# Relational vocabulary categories
RELATIONAL_CATEGORIES = [
    "kinship",      # sn (brother), snt (sister), mwt (mother), it (father)
    "reciprocal",   # dj.f n.f (he gives to him), actions requiring two parties
    "covenant",     # ꜥnḫ wḏꜣ snb (life, prosperity, health - blessing formulas)
    "exchange",     # swꜣ (trade), bꜣk (work/service)
]


def stratify_by_period(
    words: List[Dict[str, str]], 
    period_key: str = "period"
) -> Dict[EgyptianPeriod, List[Dict]]:
    """
    Stratify a word list by historical period.
    
    Args:
        words: List of word dictionaries with period information
        period_key: Key in dictionary containing period info
        
    Returns:
        Dictionary mapping periods to word lists
        
    Example:
        >>> words = [
        ...     {"word": "kꜣ", "period": "old_kingdom"},
        ...     {"word": "bꜣ", "period": "new_kingdom"}
        ... ]
        >>> stratify_by_period(words)
        {EgyptianPeriod.OLD_KINGDOM: [...], EgyptianPeriod.NEW_KINGDOM: [...]}
    """
    stratified = defaultdict(list)
    
    for word_dict in words:
        period_str = word_dict.get(period_key, "unknown").lower().replace(" ", "_")
        
        try:
            period = EgyptianPeriod(period_str)
        except ValueError:
            period = EgyptianPeriod.UNKNOWN
        
        stratified[period].append(word_dict)
    
    return dict(stratified)


def calculate_period_mar(
    words: List[str],
    bilateral_words: List[str],
    period: EgyptianPeriod
) -> Dict:
    """
    Calculate MAR for a specific period and compare to baseline.
    
    Args:
        words: All words from the period
        bilateral_words: Words identified as bilateral
        period: The historical period
        
    Returns:
        Dictionary with MAR analysis including deviation from baseline
    """
    from .analysis import calculate_mar
    
    observed_mar = calculate_mar(words, bilateral_words)
    baseline = PERIOD_MAR_BASELINE.get(period, 0.60)
    deviation = observed_mar - baseline
    
    return {
        "period": period.value,
        "observed_mar": round(observed_mar, 3),
        "baseline_mar": baseline,
        "deviation": round(deviation, 3),
        "deviation_percent": round(deviation * 100, 1),
        "interpretation": (
            "Above expected" if deviation > 0.05 else
            "At expected level" if abs(deviation) <= 0.05 else
            "Below expected"
        )
    }


def compare_relational_vocabulary(
    all_words: List[str],
    relational_words: List[str],
    bilateral_words: List[str]
) -> Dict:
    """
    Compare MAR of relational vocabulary to general vocabulary.
    
    The bilateral hypothesis predicts relational vocabulary
    maintains ~9.2% higher MAR than period baseline.
    
    Args:
        all_words: Complete vocabulary list
        relational_words: Words in relational categories
        bilateral_words: Words identified as bilateral
        
    Returns:
        Dictionary with comparative analysis
    """
    from .analysis import calculate_mar
    
    # General MAR
    general_bilateral = [w for w in bilateral_words if w not in relational_words]
    general_words = [w for w in all_words if w not in relational_words]
    general_mar = calculate_mar(general_words, general_bilateral)
    
    # Relational MAR
    relational_bilateral = [w for w in bilateral_words if w in relational_words]
    relational_mar = calculate_mar(relational_words, relational_bilateral)
    
    # Elevation
    elevation = relational_mar - general_mar
    expected_elevation = RELATIONAL_MAR_ELEVATION
    
    return {
        "general_mar": round(general_mar, 3),
        "relational_mar": round(relational_mar, 3),
        "elevation": round(elevation, 3),
        "elevation_percent": round(elevation * 100, 1),
        "expected_elevation": expected_elevation,
        "expected_elevation_percent": round(expected_elevation * 100, 1),
        "matches_prediction": abs(elevation - expected_elevation) < 0.03,
        "interpretation": (
            "Strong support for bilateral hypothesis" if elevation > 0.08 else
            "Moderate support" if elevation > 0.04 else
            "Weak or no support"
        )
    }


def analyze_stratification_trend(period_data: Dict[EgyptianPeriod, float]) -> Dict:
    """
    Analyze the trend of MAR across periods.
    
    Tests whether MAR shows declining trajectory consistent
    with transmission degradation hypothesis.
    
    Args:
        period_data: Dictionary mapping periods to observed MAR values
        
    Returns:
        Dictionary with trend analysis
    """
    # Order periods chronologically
    period_order = [
        EgyptianPeriod.OLD_KINGDOM,
        EgyptianPeriod.MIDDLE_KINGDOM,
        EgyptianPeriod.NEW_KINGDOM,
        EgyptianPeriod.LATE_PERIOD,
        EgyptianPeriod.PTOLEMAIC,
    ]
    
    values = []
    for period in period_order:
        if period in period_data:
            values.append((period.value, period_data[period]))
    
    if len(values) < 2:
        return {
            "trend": "insufficient_data",
            "periods_analyzed": len(values),
            "interpretation": "Need at least 2 periods for trend analysis"
        }
    
    # Calculate trend (simple linear)
    mars = [v[1] for v in values]
    first_mar = mars[0]
    last_mar = mars[-1]
    change = last_mar - first_mar
    
    # Check if monotonically declining
    is_declining = all(mars[i] >= mars[i+1] for i in range(len(mars)-1))
    
    return {
        "trend": "declining" if change < -0.05 else "stable" if abs(change) < 0.05 else "increasing",
        "first_period": values[0][0],
        "first_mar": first_mar,
        "last_period": values[-1][0],
        "last_mar": last_mar,
        "total_change": round(change, 3),
        "change_percent": round(change * 100, 1),
        "monotonically_declining": is_declining,
        "periods_analyzed": len(values),
        "interpretation": (
            "Strong support for degradation hypothesis" if is_declining and change < -0.1 else
            "Moderate support" if change < -0.05 else
            "Does not support degradation hypothesis"
        )
    }


def identify_stratum_boundary(words_with_mar: List[Tuple[str, float, str]]) -> Optional[float]:
    """
    Identify potential stratum boundary in vocabulary.
    
    The bilateral hypothesis predicts two strata:
    1. Words with bilateral structure carrying semantic function
    2. Words where bilateral structure is absent or decorative
    
    Args:
        words_with_mar: List of (word, mar_score, period) tuples
        
    Returns:
        MAR threshold separating strata, or None if no clear boundary
    """
    if not words_with_mar:
        return None
    
    mars = sorted([w[1] for w in words_with_mar])
    
    # Look for largest gap in MAR distribution
    max_gap = 0
    boundary = None
    
    for i in range(len(mars) - 1):
        gap = mars[i+1] - mars[i]
        if gap > max_gap:
            max_gap = gap
            boundary = (mars[i] + mars[i+1]) / 2
    
    # Only return boundary if gap is significant
    if max_gap > 0.15:
        return round(boundary, 3)
    
    return None
