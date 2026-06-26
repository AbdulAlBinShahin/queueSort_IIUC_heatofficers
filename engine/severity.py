"""Severity assignment — combines case_type, amount, and evidence."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional


def _amount_from_tx(matched_tx: Optional[dict]) -> Optional[Decimal]:
    if not matched_tx:
        return None
    amt = matched_tx.get('amount')
    try:
        return Decimal(str(amt)) if amt is not None else None
    except Exception:
        return None


def determine_severity(
    case_type: str,
    matched_tx: Optional[dict],
    complaint: str = '',
    evidence_verdict: str = 'insufficient_data',
) -> str:
    """Map a case to a severity tier.

    ``critical``  — phishing, account-takeover risk
    ``high``      — wrong_transfer, payment_failed, duplicate, agent cash-in issues, large amounts
    ``medium``    — merchant settlement, moderate amounts, inconsistent wrong-transfer
    ``low``       — generic refund, vague other, small amounts
    """
    amount = _amount_from_tx(matched_tx)

    if case_type == 'phishing_or_social_engineering':
        return 'critical'

    if case_type == 'wrong_transfer':
        if amount is not None and amount >= Decimal('10000'):
            return 'high'
        if evidence_verdict == 'inconsistent':
            return 'medium'
        return 'high'

    if case_type in ('payment_failed', 'duplicate_payment', 'agent_cash_in_issue'):
        return 'high'

    if case_type == 'merchant_settlement_delay':
        if amount is not None and amount >= Decimal('10000'):
            return 'high'
        return 'medium'

    if case_type == 'refund_request':
        if amount is not None and amount >= Decimal('10000'):
            return 'high'
        return 'low'

    # 'other' and anything not covered
    if amount is not None:
        if amount >= Decimal('10000'):
            return 'high'
        if amount >= Decimal('1000'):
            return 'medium'
        return 'low'

    return 'low'