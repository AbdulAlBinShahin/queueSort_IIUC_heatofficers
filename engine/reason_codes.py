"""Assemble the ``reason_codes`` array — short labels explaining the decision."""

from __future__ import annotations

from typing import Iterable, List, Optional


def _has_dup_amount(txs: list[dict], matched_tx: dict) -> bool:
    target_amt = matched_tx.get('amount')
    target_cp  = matched_tx.get('counterparty')
    for t in txs:
        if t is matched_tx:
            continue
        if t.get('amount') == target_amt and t.get('counterparty') == target_cp:
            return True
    return False


def build_reason_codes(
    case_type: str,
    evidence_verdict: str,
    matched_tx: Optional[dict],
    all_transactions: Iterable[dict],
) -> List[str]:
    codes: List[str] = []

    if matched_tx is not None:
        codes.append('transaction_match')
    else:
        codes.append('no_transaction_match')

    if evidence_verdict == 'consistent':
        codes.append('evidence_consistent')
    elif evidence_verdict == 'inconsistent':
        codes.append('evidence_inconsistent')
    else:
        codes.append('insufficient_data')

    if matched_tx and matched_tx.get('counterparty'):
        codes.append('counterparty_signal')

    if matched_tx is not None:
        try:
            amt = matched_tx.get('amount')
            if amt is not None and float(amt) > 10000:
                codes.append('high_value')
        except Exception:
            pass

    if case_type == 'phishing_or_social_engineering':
        codes.append('phishing_detected')
    if case_type == 'duplicate_payment' and matched_tx is not None \
            and _has_dup_amount(list(all_transactions), matched_tx):
        codes.append('duplicate_amount_counterparty')
    if case_type == 'payment_failed' and matched_tx is not None \
            and (matched_tx.get('status') or '').lower() == 'completed':
        codes.append('status_completed_contradicts_failed')

    # Deduplicate while preserving order.
    seen = set()
    unique: List[str] = []
    for c in codes:
        if c not in seen:
            unique.append(c)
            seen.add(c)
    return unique