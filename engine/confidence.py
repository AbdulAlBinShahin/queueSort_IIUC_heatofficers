"""Confidence scoring — based on how many signals the engine could match."""

from __future__ import annotations

from typing import Optional


_BASE = 0.55
_STEP = 0.08
_CAP  = 0.97
_FLOOR = 0.40


def calculate_confidence(
    matched_tx: Optional[dict],
    evidence_verdict: str,
    case_type: str,
) -> float:
    """Heuristic confidence score in ``[0.0, 1.0]``."""
    score = _BASE

    if matched_tx is not None:
        score += _STEP  # transaction match
    if matched_tx and matched_tx.get('counterparty'):
        score += _STEP  # counterparty signal
    if evidence_verdict == 'consistent':
        score += _STEP
    elif evidence_verdict == 'inconsistent':
        score -= _STEP / 2  # contradictory evidence lowers confidence
    # Phishing / social-engineering cases are high-signal because of keywords,
    # even without a transaction match.
    if case_type == 'phishing_or_social_engineering':
        score += _STEP

    return round(max(_FLOOR, min(_CAP, score)), 2)