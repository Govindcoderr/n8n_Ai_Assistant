
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple


def _similarity(a: str, b: str) -> float:
    """Return similarity score between two strings (0–100)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100


def sublimeSearch(
    query: str,
    items: List[Dict[str, Any]],
    keys: List[str],
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Fuzzy search implementation similar to sublimeSearch in TS

    Returns:
        List of tuples: (item, score)
    """

    if not query or not items:
        return []

    results: List[Tuple[Dict[str, Any], float]] = []

    for item in items:
        best_score = 0.0

        for key in keys:
            value = item.get(key)

            if not value:
                continue

            # Handle list values (e.g., tags, keywords)
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, str):
                        best_score = max(best_score, _similarity(query, v))

            # Handle string values
            elif isinstance(value, str):
                best_score = max(best_score, _similarity(query, value))

        if best_score > 0:
            results.append((item, best_score))

    # Sort by score descending (most relevant first)
    results.sort(key=lambda x: x[1], reverse=True)

    return results


