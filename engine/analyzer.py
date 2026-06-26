"""Top-level orchestrator — runs all engine sub-modules in order.

This is the only function the views layer needs to call.
"""

from __future__ import annotations

from typing import Any

from . import actions, classifier, confidence, escalation, reason_codes, replies, \
             router, safety, severity, summarizer, verdict
from .matcher import find_relevant_transaction


def analyze(ticket_data: dict) -> dict:
    """Run the rule engine end-to-end and return the spec-shaped response dict."""
    complaint    = ticket_data.get('complaint', '') or ''
    user_type    = ticket_data.get('user_type') or 'unknown'
    language     = ticket_data.get('language') or 'en'
    transactions = list(ticket_data.get('transaction_history') or [])

    matched_tx = find_relevant_transaction(complaint, transactions)
    case_type  = classifier.classify_case_type(complaint, user_type, matched_tx)
    evidence_verdict = verdict.determine_evidence_verdict(
        complaint, matched_tx, transactions, case_type,
    )
    sev  = severity.determine_severity(case_type, matched_tx, complaint, evidence_verdict)
    dept = router.determine_department(case_type, sev, user_type)

    agent_summary  = summarizer.generate_agent_summary(case_type, matched_tx)
    next_action    = actions.generate_next_action(case_type, matched_tx)
    customer_reply = replies.generate_customer_reply(case_type, matched_tx, language)

    # Safety check on the customer reply — raises if anything slipped through.
    safety.enforce_safety(customer_reply)

    human_review = escalation.requires_human_review(
        case_type=case_type,
        severity=sev,
        evidence_verdict=evidence_verdict,
        matched_tx=matched_tx,
        complaint=complaint,
    )

    conf  = confidence.calculate_confidence(matched_tx, evidence_verdict, case_type)
    codes = reason_codes.build_reason_codes(
        case_type, evidence_verdict, matched_tx, transactions,
    )

    return {
        'ticket_id':               ticket_data['ticket_id'],
        'relevant_transaction_id': (matched_tx or {}).get('transaction_id'),
        'evidence_verdict':        evidence_verdict,
        'case_type':               case_type,
        'severity':                sev,
        'department':              dept,
        'agent_summary':           agent_summary,
        'recommended_next_action': next_action,
        'customer_reply':          customer_reply,
        'human_review_required':   human_review,
        'confidence':              conf,
        'reason_codes':            codes,
    }