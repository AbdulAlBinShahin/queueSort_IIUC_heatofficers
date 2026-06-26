"""Operational next steps for the support agent.

These are *recommendations*, never commitments. They never promise
refunds, reversals, or account actions — that authority sits with the
human review team.
"""

from __future__ import annotations

from typing import Optional


NEXT_ACTION_TEMPLATES = {
    'wrong_transfer':
        "Verify {tx_id} details with the customer and initiate the wrong-transfer "
        "dispute workflow per policy. Do not promise recovery.",
    'payment_failed':
        "Investigate ledger status for {tx_id}. If balance was deducted on a "
        "failed payment, escalate to payments_ops for review per standard SLA. "
        "Do not confirm a refund.",
    'refund_request':
        "Inform the customer that refund eligibility depends on the merchant's "
        "own policy and provide guidance on contacting the merchant directly.",
    'duplicate_payment':
        "Verify the duplicate with payments_ops using {tx_id}. If the biller "
        "confirms only one payment was received, request a reversal review for "
        "the duplicate.",
    'merchant_settlement_delay':
        "Route to merchant_operations to verify settlement batch status for "
        "{tx_id} and share a revised ETA once available.",
    'agent_cash_in_issue':
        "Investigate {tx_id} with agent_operations. Confirm settlement state and "
        "resolve within the standard cash-in SLA. Do not credit the wallet "
        "manually.",
    'phishing_or_social_engineering':
        "Escalate to fraud_risk immediately. Confirm to the customer that the "
        "company never asks for OTP, PIN, or password, and log the reported "
        "contact for fraud-pattern analysis.",
    'other':
        "Reply to the customer asking for the specific transaction, amount, "
        "and what went wrong so the case can be reclassified.",
}

DEFAULT_ACTION = (
    "Acknowledge the complaint, request additional details, and route to the "
    "appropriate team once enough context is available."
)


def _fmt_tx(matched_tx: Optional[dict]) -> str:
    if matched_tx and matched_tx.get('transaction_id'):
        return str(matched_tx['transaction_id'])
    return 'the reported transaction'


def generate_next_action(case_type: str, matched_tx: Optional[dict]) -> str:
    template = NEXT_ACTION_TEMPLATES.get(case_type, DEFAULT_ACTION)
    return template.format(tx_id=_fmt_tx(matched_tx))