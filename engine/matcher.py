"""Match a complaint to a single transaction from the provided history.

Heuristic score-based approach — no ML. Returns the transaction that
matches the most signals, or ``None`` when nothing matches.
"""

from __future__ import annotations

import re
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from .keywords import (
    PAYMENT_FAILED_EN, PAYMENT_FAILED_BN, PAYMENT_FAILED_BANGLISH,
    AGENT_CASH_IN_EN, AGENT_CASH_IN_BN, AGENT_CASH_IN_BANGLISH,
    MERCHANT_SETTLEMENT_EN, MERCHANT_SETTLEMENT_BANGLISH,
    WRONG_TRANSFER_EN, WRONG_TRANSFER_BN, WRONG_TRANSFER_BANGLISH,
    DUPLICATE_EN, DUPLICATE_BANGLISH,
    any_match,
)


# ---------------------------------------------------------------------------
# Amount + time extraction
# ---------------------------------------------------------------------------

_AMOUNT_RE = re.compile(
    r'(?P<amt>\d{1,3}(?:[,\s]\d{3})+|\d+(?:\.\d+)?)'
    r'\s*(?:taka|tk|bdt|৳|টাকা)?',
    flags=re.IGNORECASE,
)
_TIME_KEYWORDS = {
    'today':     0,
    'yesterday': 1,
    'morning':   0,
    'evening':   0,
    'night':     0,
    'noon':      0,
    'afternoon': 0,
}


def extract_amounts(text: str) -> list[Decimal]:
    """Return all plausible amount numbers in the complaint, in order."""
    found: list[Decimal] = []
    for m in _AMOUNT_RE.finditer(text or ''):
        raw = m.group('amt').replace(',', '').replace(' ', '')
        try:
            found.append(Decimal(raw))
        except Exception:
            continue
    return found


def extract_time_keywords(text: str) -> list[str]:
    text_lower = (text or '').lower()
    return [kw for kw in _TIME_KEYWORDS if kw in text_lower]


# ---------------------------------------------------------------------------
# Complaint intent → expected transaction type
# ---------------------------------------------------------------------------

def expected_tx_type(complaint_lower: str) -> Optional[str]:
    """Map complaint signals to a likely ``type`` field value, or ``None``."""
    if any_match(complaint_lower, MERCHANT_SETTLEMENT_EN + MERCHANT_SETTLEMENT_BANGLISH):
        return 'settlement'
    if any_match(complaint_lower, AGENT_CASH_IN_EN + AGENT_CASH_IN_BN + AGENT_CASH_IN_BANGLISH):
        return 'cash_in'
    if any_match(complaint_lower, DUPLICATE_EN + DUPLICATE_BANGLISH):
        return 'payment'
    if any_match(complaint_lower, PAYMENT_FAILED_EN + PAYMENT_FAILED_BN + PAYMENT_FAILED_BANGLISH):
        return 'payment'
    if any_match(complaint_lower, WRONG_TRANSFER_EN + WRONG_TRANSFER_BN + WRONG_TRANSFER_BANGLISH):
        return 'transfer'
    return None


def complaint_implies_failure(complaint_lower: str) -> bool:
    """True if complaint suggests a failed/unsuccessful transaction."""
    return any_match(
        complaint_lower,
        PAYMENT_FAILED_EN + PAYMENT_FAILED_BN + PAYMENT_FAILED_BANGLISH,
    )


def complaint_implies_wrong(complaint_lower: str) -> bool:
    return any_match(
        complaint_lower,
        WRONG_TRANSFER_EN + WRONG_TRANSFER_BN + WRONG_TRANSFER_BANGLISH,
    )


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def _normalise_tx(tx: dict) -> dict:
    """Coerce a transaction dict into the shape the engine expects."""
    amount = tx.get('amount')
    try:
        amount = Decimal(str(amount)) if amount is not None else Decimal('0')
    except Exception:
        amount = Decimal('0')
    return {
        'transaction_id': tx.get('transaction_id', ''),
        'timestamp':      tx.get('timestamp'),
        'type':           tx.get('type', ''),
        'amount':         amount,
        'counterparty':   tx.get('counterparty', '') or '',
        'status':         tx.get('status', ''),
    }


def _amount_score(complaint_amounts: list[Decimal], tx_amount: Decimal) -> int:
    if not complaint_amounts:
        return 0
    if tx_amount in complaint_amounts:
        return 3
    # Approximate match (within 5% or 5 BDT).
    for ca in complaint_amounts:
        if abs(ca - tx_amount) <= max(Decimal('5'), tx_amount * Decimal('0.05')):
            return 2
    return 0


def _time_score(complaint_times: list[str], tx_timestamp) -> int:
    if not complaint_times or tx_timestamp is None:
        return 0
    # "today" / "yesterday" are the only time signals we model — they
    # loosely confirm the transaction is recent, which is enough.
    if 'today' in complaint_times or 'yesterday' in complaint_times:
        return 1
    return 0


def _type_score(expected: Optional[str], tx_type: str) -> int:
    if expected and tx_type and expected == tx_type:
        return 2
    return 0


def _counterparty_score(complaint_lower: str, counterparty: str) -> int:
    if not counterparty:
        return 0
    cp = str(counterparty).lower()
    if cp and cp in complaint_lower:
        return 2
    # Phone-number style match — last 7 digits.
    digits = ''.join(ch for ch in cp if ch.isdigit())
    if len(digits) >= 7 and digits[-7:] in ''.join(ch for ch in complaint_lower if ch.isdigit()):
        return 2
    return 0


def _status_score(complaint_lower: str, tx_status: str) -> int:
    if not tx_status:
        return 0
    s = tx_status.lower()
    if s == 'failed' and complaint_implies_failure(complaint_lower):
        return 1
    if s == 'completed' and complaint_implies_failure(complaint_lower):
        # Negative signal: complaint says failed but txn shows completed.
        return -1
    if s == 'pending' and ('not reflected' in complaint_lower or 'ashe nai' in complaint_lower):
        return 1
    return 0


def score_transaction(complaint: str, tx: dict) -> tuple[int, dict]:
    """Return (score, normalised_tx). Higher score = better match."""
    ntx = _normalise_tx(tx)
    complaint_lower = (complaint or '').lower()

    amounts = extract_amounts(complaint_lower)
    times = extract_time_keywords(complaint_lower)
    expected = expected_tx_type(complaint_lower)

    total = 0
    total += _amount_score(amounts, ntx['amount'])
    total += _time_score(times, ntx['timestamp'])
    total += _type_score(expected, ntx['type'])
    total += _counterparty_score(complaint_lower, ntx['counterparty'])
    total += _status_score(complaint_lower, ntx['status'])
    return total, ntx


def find_relevant_transaction(complaint: str, transactions) -> Optional[dict]:
    """Pick the single best transaction, or ``None``.

    Returns the transaction dict in the engine's internal shape. Negative
    scores are clamped to zero — a contradictory transaction is treated
    as a weak signal, not an automatic disqualifier, so we let
    ``verdict.py`` decide whether the evidence is truly inconsistent.
    """
    if not transactions:
        return None

    best_score = 0
    best_tx: Optional[dict] = None

    for tx in transactions:
        score, ntx = score_transaction(complaint, tx)
        if score < 0:
            score = 0
        # Tie-break by recency (later timestamp wins).
        if score > best_score or (
            score == best_score and best_tx is not None
            and (ntx['timestamp'] or '') > (best_tx['timestamp'] or '')
            and score > 0
        ):
            best_score = score
            best_tx = ntx

    return best_tx