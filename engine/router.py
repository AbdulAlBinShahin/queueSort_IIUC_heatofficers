"""Department routing — maps case_type (+ severity + user_type) to a team."""

from __future__ import annotations


CASE_TYPE_TO_DEPARTMENT = {
    'wrong_transfer':                  'dispute_resolution',
    'payment_failed':                  'payments_ops',
    'refund_request':                  'customer_support',   # may upgrade if severity=high
    'duplicate_payment':               'payments_ops',
    'merchant_settlement_delay':       'merchant_operations',
    'agent_cash_in_issue':             'agent_operations',
    'phishing_or_social_engineering':  'fraud_risk',
    'other':                           'customer_support',
}


def determine_department(case_type: str, severity: str = '', user_type: str = '') -> str:
    """Return the department enum value for the given case."""
    base = CASE_TYPE_TO_DEPARTMENT.get(case_type, 'customer_support')

    # Promote refund cases to dispute resolution when they have real financial impact.
    if case_type == 'refund_request' and severity in ('high', 'critical'):
        return 'dispute_resolution'

    return base