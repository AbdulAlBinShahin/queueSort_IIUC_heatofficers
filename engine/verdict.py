"""Decide whether the matched transaction supports, contradicts, or fails
to confirm the customer's complaint.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from .keywords import (
    PAYMENT_FAILED_EN, PAYMENT_FAILED_BN, PAYMENT_FAILED_BANGLISH,
    WRONG_TRANSFER_EN, WRONG_TRANSFER_BN, WRONG_TRANSFER_BANGLISH,
    DUPLICATE_EN, DUPLICATE_BANGLISH,
    any_match,
)


def _lower(text: Optional[str]) -> str:
    return (text or '').lower()


def determine_evidence_verdict(
    complaint: str,
    matched_tx: Optional[dict],
    all_transactions: list[dict],
    case_type: str,
) -> str:
    """Return ``'consistent'``, ``'inconsistent'``, or ``'insufficient_data'``."""

    # No transaction history at all.
    if not all_transactions:
        return 'insufficient_data'

    # No plausible match — we cannot confirm or deny.
    if matched_tx is None:
        return 'insufficient_data'

    complaint_lower = _lower(complaint)

    # --- Case-specific contradictions -----------------------------------

    if case_type == 'payment_failed':
        status = (matched_tx.get('status') or '').lower()
        # Complaint implies failure but status is 'completed' → contradiction.
        if status == 'completed':
            return 'inconsistent'
        # Status is failed/pending/reversed → consistent with complaint.
        if status in ('failed', 'pending', 'reversed'):
            return 'consistent'
        # No status info → inconclusive.
        return 'insufficient_data'

    if case_type == 'wrong_transfer':
        cp = (matched_tx.get('counterparty') or '').strip()
        # If the same counterparty appears in 2+ prior transactions, the
        # customer has previously used this number — unlikely to be a typo.
        if cp:
            same = [
                t for t in all_transactions
                if (t.get('counterparty') or '').strip() == cp
            ]
            if len(same) >= 2:
                return 'inconsistent'

        # Default: a completed transfer to the claimed counterparty is
        # consistent with "I sent to the wrong person."
        if (matched_tx.get('status') or '').lower() == 'completed':
            return 'consistent'
        return 'consistent'

    if case_type == 'duplicate_payment':
        # Two identical transactions to the same counterparty within 60s
        # are the canonical "duplicate payment" signal.
        target_amt = matched_tx.get('amount')
        target_cp = matched_tx.get('counterparty')
        target_ts = matched_tx.get('timestamp')

        for t in all_transactions:
            if t is matched_tx:
                continue
            if (t.get('counterparty') or '') == target_cp \
                    and t.get('amount') == target_amt \
                    and target_ts and t.get('timestamp') \
                    and abs((t['timestamp'] - target_ts).total_seconds()) <= 60:
                return 'consistent'
        # No duplicate found → complaint is inconsistent with the data.
        return 'inconsistent'

    if case_type == 'agent_cash_in_issue':
        status = (matched_tx.get('status') or '').lower()
        if status == 'completed':
            return 'inconsistent'
        if status in ('pending', 'failed'):
            return 'consistent'
        return 'insufficient_data'

    if case_type == 'merchant_settlement_delay':
        status = (matched_tx.get('status') or '').lower()
        if status == 'completed':
            return 'inconsistent'
        return 'consistent'

    if case_type == 'phishing_or_social_engineering':
        # Phishing reports are independent of the transaction ledger.
        return 'insufficient_data'

    # refund_request / other — neutral; match existence is consistent enough.
    return 'consistent'