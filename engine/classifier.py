"""Rule-based ``case_type`` classifier.

Priority order matters — phishing must beat wrong_transfer so that
"someone called me and asked for my OTP after I sent money" still
routes to fraud_risk.
"""

from __future__ import annotations

from typing import Optional

from .keywords import (
    PHISHING_EN, PHISHING_BN, PHISHING_BANGLISH,
    AGENT_CASH_IN_EN, AGENT_CASH_IN_BN, AGENT_CASH_IN_BANGLISH,
    MERCHANT_SETTLEMENT_EN, MERCHANT_SETTLEMENT_BANGLISH,
    DUPLICATE_EN, DUPLICATE_BANGLISH,
    PAYMENT_FAILED_EN, PAYMENT_FAILED_BN, PAYMENT_FAILED_BANGLISH,
    WRONG_TRANSFER_EN, WRONG_TRANSFER_BN, WRONG_TRANSFER_BANGLISH,
    REFUND_EN, REFUND_BN, REFUND_BANGLISH,
    any_match,
)


# Priority-ordered classifier chain. First match wins.
_CLASSIFIER_CHAIN = [
    ('phishing_or_social_engineering', PHISHING_EN + PHISHING_BN + PHISHING_BANGLISH),
    ('agent_cash_in_issue',            AGENT_CASH_IN_EN + AGENT_CASH_IN_BN + AGENT_CASH_IN_BANGLISH),
    ('merchant_settlement_delay',      MERCHANT_SETTLEMENT_EN + MERCHANT_SETTLEMENT_BANGLISH),
    ('duplicate_payment',              DUPLICATE_EN + DUPLICATE_BANGLISH),
    ('payment_failed',                 PAYMENT_FAILED_EN + PAYMENT_FAILED_BN + PAYMENT_FAILED_BANGLISH),
    ('wrong_transfer',                 WRONG_TRANSFER_EN + WRONG_TRANSFER_BN + WRONG_TRANSFER_BANGLISH),
    ('refund_request',                 REFUND_EN + REFUND_BN + REFUND_BANGLISH),
]


def _user_is_merchant(user_type: str) -> bool:
    return (user_type or '').lower() == 'merchant'


def classify_case_type(
    complaint: str,
    user_type: str = 'unknown',
    matched_tx: Optional[dict] = None,
) -> str:
    """Return the case_type enum value as a string."""
    complaint_lower = (complaint or '').lower()

    # Merchant-portal / merchant-user + settlement keywords → settlement delay.
    if _user_is_merchant(user_type):
        if any_match(complaint_lower, MERCHANT_SETTLEMENT_EN + MERCHANT_SETTLEMENT_BANGLISH):
            return 'merchant_settlement_delay'

    for case_type, keywords in _CLASSIFIER_CHAIN:
        if any_match(complaint_lower, keywords):
            return case_type

    # Fallback — but if there is any signal of a problem, default to refund.
    if any_match(complaint_lower, REFUND_EN + REFUND_BN + REFUND_BANGLISH):
        return 'refund_request'

    return 'other'