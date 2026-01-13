"""Bilateral compound analysis."""

from typing import List, Dict, Tuple

PROTO_PHONEMES = {
    "BA": {"phoneme": "b", "meaning": "soul-container"},
    "DA": {"phoneme": "d", "meaning": "hand/give"},
    "HA": {"phoneme": "h", "meaning": "breath/descend"},
    "KA": {"phoneme": "k", "meaning": "vital force"},
    "LA": {"phoneme": "l", "meaning": "tongue/extension"},
    "MA": {"phoneme": "m", "meaning": "water/mother"},
    "NA": {"phoneme": "n", "meaning": "negation/toward"},
    "RA": {"phoneme": "r", "meaning": "mouth/sun"},
    "SHA": {"phoneme": "š", "meaning": "pool/garden"},
    "TA": {"phoneme": "t", "meaning": "bread/earth"},
    "WA": {"phoneme": "w", "meaning": "one/uniqueness"},
}

COVENANT_STATUS = {
    "intact": "Bilateral structure preserved, reciprocal meaning accessible",
    "externalized": "Covenant axis projected outward, relational meaning",
    "collapsed": "Bilateral structure degraded, unilateral reading only",
    "contaminated": "Mixed bilateral/non-bilateral elements"
}


def extract_proto_phonemes(word: str) -> List[str]:
    """Extract proto-phonemes present in a word."""
    found = []
    word_lower = word.lower()
    for name, info in PROTO_PHONEMES.items():
        if info["phoneme"] in word_lower:
            found.append(name)
    return found


def analyze_compound(word: str, meaning: str = None) -> Dict:
    """Perform full bilateral analysis on a compound word."""
    from .analysis import analyze_ayin_position
    
    ayin_analysis = analyze_ayin_position(word)
    proto_phonemes = extract_proto_phonemes(word)
    
    if ayin_analysis["is_medial"]:
        covenant_status = "intact"
    elif ayin_analysis["has_ayin"]:
        covenant_status = "externalized"
    elif proto_phonemes:
        covenant_status = "collapsed"
    else:
        covenant_status = "contaminated"
    
    return {
        "word": word,
        "meaning": meaning,
        "forward": word,
        "reverse": word[::-1],
        "proto_phonemes": proto_phonemes,
        "has_ayin": ayin_analysis["has_ayin"],
        "ayin_medial": ayin_analysis["is_medial"],
        "covenant_status": covenant_status,
    }


def assess_covenant_status(word: str) -> Tuple[str, str]:
    """Assess the covenant status of a word."""
    from .analysis import analyze_ayin_position
    
    ayin = analyze_ayin_position(word)
    protos = extract_proto_phonemes(word)
    
    if ayin["is_medial"]:
        return ("intact", COVENANT_STATUS["intact"])
    elif ayin["has_ayin"]:
        return ("externalized", COVENANT_STATUS["externalized"])
    elif protos:
        return ("collapsed", COVENANT_STATUS["collapsed"])
    return ("contaminated", COVENANT_STATUS["contaminated"])
