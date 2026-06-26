"""Generate the 1–2 sentence ``agent_summary`` from a matched transaction."""

from __future__ import annotations

from typing import Optional


AGENT_SUMMARY_TEMPLATES = {
    'wrong_transfer':
        "Customer reports sending {amount} BDT via {tx_id} to {counterparty}, "
        "which they believe was the wrong recipient.",
    'payment_failed':
        "Customer attempted a {amount} BDT payment ({tx_id}) which shows as "
        "'{status}', but reports balance was deducted.",
    'refund_request':
        "Customer requests a refund of {amount} BDT for transaction {tx_id}. "
        "No service failure is explicitly claimed.",
    'duplicate_payment':
        "Possible duplicate payment: two identical {amount} BDT transactions to "
        "{counterparty} within a short window.",
    'merchant_settlement_delay':
        "Merchant reports {amount} BDT settlement ({tx_id}) is delayed beyond "
        "the expected window. Status: {status}.",
    'agent_cash_in_issue':
        "Customer reports {amount} BDT cash-in via agent {counterparty} ({tx_id}) "
        "was not reflected in their wallet balance. Status: {status}.",
    'phishing_or_social_engineering':
        "Customer reports an unsolicited contact requesting credentials or "
        "personal information.",
    'other':
        "Customer reports a general concern. Available transaction history does "
        "not provide enough detail to classify further.",
}

DEFAULT_SUMMARY = (
    "Customer raised a complaint; available context is insufficient to classify "
    "with high confidence."
)


def _fmt_amount(amt) -> str:
    if amt is None or amt == '':
        return 'an unspecified'
    try:
        return f"{amt:,.0f}"
    except Exception:
        return str(amt)


def _fmt_counterparty(cp) -> str:
    cp = (cp or '').strip()
    return cp if cp else 'an unspecified recipient'


def generate_agent_summary(case_type: str, matched_tx: Optional[dict]) -> str:
    template = AGENT_SUMMARY_TEMPLATES.get(case_type, DEFAULT_SUMMARY)

    if matched_tx is None:
        # Provide a useful string even without a matched transaction.
        if case_type == 'phishing_or_social_engineering':
            return AGENT_SUMMARY_TEMPLATES['phishing_or_social_engineering']
        if case_type == 'merchant_settlement_delay':
            return "Merchant reports a settlement delay; no matching settlement was located in the provided history."
        if case_type == 'refund_request':
            return "Customer requests a refund; no specific transaction is referenced in the provided history."
        if case_type == 'agent_cash_in_issue':
            return "Customer reports an agent cash-in was not reflected; no matching cash-in transaction was located."
        return "Customer raised a concern; no matching transaction was located in the provided history."

    return template.format(
        amount=_fmt_amount(matched_tx.get('amount')),
        tx_id=matched_tx.get('transaction_id') or 'unknown',
        counterparty=_fmt_counterparty(matched_tx.get('counterparty')),
        status=matched_tx.get('status') or 'unknown',
    )