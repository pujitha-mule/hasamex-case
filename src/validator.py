import re
from typing import List, Dict, Iterable, Tuple

# [Expert, Market, MM:SS]
CITATION_RE = re.compile(
    r"\[([^,\]]+),\s*([^,\]]+),\s*(\d{2}:\d{2})\]"
)

def _norm(s: str) -> str:
    return " ".join((s or "").split())

def validate_quotes_against_turns(
    quotes: Iterable[Dict],
    turns: List[Dict],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate that each quote is a verbatim substring of the text of the
    SPECIFIC (expert, timestamp) turn it cites.

    `turns` must be dicts with keys:
        {"expert": "...", "timestamp": "MM:SS", "speaker": "...", "text": "..."}
    """
    by_key = {(t["expert"], t["timestamp"]): t for t in turns}

    valid, rejected = [], []
    for q in quotes or []:
        key = (q.get("expert"), q.get("timestamp"))
        text = _norm(q.get("text"))
        turn = by_key.get(key)
        if turn and text and text in _norm(turn["text"]):
            valid.append(q)
        else:
            rejected.append(q)
    return valid, rejected

def extract_citations(answer: str) -> List[Tuple[str, str, str]]:
    """Return list of (expert, market, timestamp) tuples found in the answer."""
    if not answer:
        return []
    return [(m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
            for m in CITATION_RE.finditer(answer)]

def validate_answer_has_citation(answer: str) -> bool:
    """True if the answer contains at least one [Expert, Market, MM:SS] citation."""
    return bool(CITATION_RE.search(answer or ""))

def validate_citations_in_evidence(
    answer: str,
    turns: List[Dict],
) -> Tuple[bool, List[Tuple[str, str, str]]]:
    """
    Every citation in the answer must match a retrieved turn on
    (expert, timestamp). The market in the citation is checked against the
    turn's market too.

    Returns (all_valid, valid_citations).
    """
    cites = extract_citations(answer)
    if not cites:
        return False, []

    by_key = {(t["expert"], t["timestamp"]): t for t in turns}
    valid = []
    for expert, market, ts in cites:
        turn = by_key.get((expert, ts))
        if turn and turn.get("market") == market:
            valid.append((expert, market, ts))
    return len(valid) == len(cites) and len(valid) > 0, valid