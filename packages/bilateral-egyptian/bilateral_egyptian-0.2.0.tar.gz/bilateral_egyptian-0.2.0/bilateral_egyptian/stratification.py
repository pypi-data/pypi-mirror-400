"""Stratification analysis for bilateral Egyptian texts."""

from typing import List, Dict
from collections import defaultdict
from enum import Enum


class EgyptianPeriod(Enum):
    OLD_KINGDOM = "old_kingdom"
    MIDDLE_KINGDOM = "middle_kingdom"
    NEW_KINGDOM = "new_kingdom"
    LATE_PERIOD = "late_period"
    PTOLEMAIC = "ptolemaic"
    UNKNOWN = "unknown"


PERIOD_MAR_BASELINE = {
    EgyptianPeriod.OLD_KINGDOM: 0.72,
    EgyptianPeriod.MIDDLE_KINGDOM: 0.68,
    EgyptianPeriod.NEW_KINGDOM: 0.60,
    EgyptianPeriod.LATE_PERIOD: 0.54,
    EgyptianPeriod.PTOLEMAIC: 0.48,
}


def stratify_by_period(words: List[Dict], period_key: str = "period") -> Dict[EgyptianPeriod, List[Dict]]:
    """Stratify a word list by historical period."""
    stratified = defaultdict(list)
    for word_dict in words:
        period_str = word_dict.get(period_key, "unknown").lower().replace(" ", "_")
        try:
            period = EgyptianPeriod(period_str)
        except ValueError:
            period = EgyptianPeriod.UNKNOWN
        stratified[period].append(word_dict)
    return dict(stratified)


def calculate_period_mar(words: List[str], bilateral_words: List[str], period: EgyptianPeriod) -> Dict:
    """Calculate MAR for a specific period and compare to baseline."""
    from .analysis import calculate_mar
    
    observed_mar = calculate_mar(words, bilateral_words)
    baseline = PERIOD_MAR_BASELINE.get(period, 0.60)
    deviation = observed_mar - baseline
    
    return {
        "period": period.value,
        "observed_mar": round(observed_mar, 3),
        "baseline_mar": baseline,
        "deviation": round(deviation, 3),
    }


def compare_relational_vocabulary(all_words: List[str], relational_words: List[str], bilateral_words: List[str]) -> Dict:
    """Compare MAR of relational vocabulary to general vocabulary."""
    from .analysis import calculate_mar
    
    general_words = [w for w in all_words if w not in relational_words]
    general_bilateral = [w for w in bilateral_words if w not in relational_words]
    general_mar = calculate_mar(general_words, general_bilateral)
    
    relational_bilateral = [w for w in bilateral_words if w in relational_words]
    relational_mar = calculate_mar(relational_words, relational_bilateral)
    
    return {
        "general_mar": round(general_mar, 3),
        "relational_mar": round(relational_mar, 3),
        "elevation": round(relational_mar - general_mar, 3),
    }
