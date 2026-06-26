"""Decide whether a ticket requires human review before any action is taken."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional


def requires_human_review(
    case_type: str,
    severity: str,
    evidence_verdict: str,
    matched_tx: Optional[dict] = None,
    complaint: str = '',
) -> bool:
    """Return True if the case is risky / uncertain / high-impact.

    Mirrors the system spec's escalation rules.
    """
    # 1. Disputes always need a human.
    if case_type in (
        'wrong_transfer',
        'phishing_or_social_engineering',
        'duplicate_payment',
        'merchant_settlement_delay',
        'agent_cash_in_issue',
    ):
        return True

    # 2. Conflicting or insufficient evidence always escalates.
    if evidence_verdict in ('inconsistent', 'insufficient_data'):
        return True

    # 3. High / critical severity always escalates.
    if severity in ('high', 'critical'):
        return True

    # 4. Large amounts escalate even on a refund_request.
    if matched_tx:
        try:
            amount = Decimal(str(matched_tx.get('amount') or 0))
        except Exception:
            amount = Decimal('0')
        if amount > Decimal('10000'):
            return True

    # 5. Refund request with a credible threat / legal mention escalates.
    complaint_lower = (complaint or '').lower()
    legal_markers = [
        'lawyer', 'court', 'legal action', 'consumer rights',
        'বিচার', 'আইন', 'আদালত', 'উকিল', 'consumer court',
    ]
    if any(m in complaint_lower for m in legal_markers):
        return True

    return False