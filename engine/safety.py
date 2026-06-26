"""Safety enforcement — detects injection attempts and audits generated text.

Two responsibilities:

1. ``detect_injection(text)`` — flag obvious prompt-injection patterns
   in complaint text so they can be logged and ignored.
2. ``check_safety_violations(text)`` / ``enforce_safety(text)`` — audit
   generated ``customer_reply`` strings for the four safety rules.
"""

from __future__ import annotations

import re
from typing import List


# ---------------------------------------------------------------------------
# Prompt-injection detection
# ---------------------------------------------------------------------------

INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(all\s+|previous\s+|your\s+)?(instructions|rules|guidelines)', re.I),
    re.compile(r'\byou\s+are\s+now\b', re.I),
    re.compile(r'\bdisregard\b', re.I),
    re.compile(r'pretend\s+(you\s+are|to\s+be)', re.I),
    re.compile(r'\bsystem\s+prompt\b', re.I),
    re.compile(r'\bconfirm\s+(a\s+|the\s+)?refund\b', re.I),
    re.compile(r'\bpromise\b.*\brefund\b', re.I),
    re.compile(r'\breveal\s+(your\s+|the\s+)?prompt\b', re.I),
    re.compile(r'\bbypass\b.*\b(rule|safety|guard)', re.I),
]


def detect_injection(text: str) -> bool:
    """Return True if the complaint text looks like an injection attempt."""
    if not text:
        return False
    for pat in INJECTION_PATTERNS:
        if pat.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Customer-reply safety scanning
# ---------------------------------------------------------------------------

# Patterns that would make a customer reply unsafe.
BANNED_PHRASES = [
    re.compile(r'\bsend\s+(me|us)\s+your\s+(pin|otp|password|cvv)\b', re.I),
    re.compile(r'\bshare\s+(your\s+)?(pin|otp|password|cvv)\b', re.I),
    re.compile(r'\btell\s+(me|us)\s+your\s+(pin|otp|password|cvv)\b', re.I),
    re.compile(r'\bprovide\s+(your\s+)?(pin|otp|password|cvv)\b', re.I),
    re.compile(r'\bwe\s+will\s+refund\b', re.I),
    re.compile(r'\bwe\s+will\s+reverse\b', re.I),
    re.compile(r'\bmoney\s+will\s+be\s+returned\b', re.I),
    re.compile(r'\baccount\s+will\s+be\s+unblocked\b', re.I),
    re.compile(r'\bwill\s+be\s+credited\s+back\b', re.I),
    re.compile(r'\bguarantee(d)?\s+refund\b', re.I),
    # Direct third-party phone numbers (rough heuristic — long BD-style mobile numbers).
    re.compile(r'\b01[3-9]\d{8}\b'),
    re.compile(r'\b\+?8801[3-9]\d{8}\b'),
]


def check_safety_violations(text: str) -> List[str]:
    """Return a list of human-readable violations found in ``text``."""
    if not text:
        return []
    violations: List[str] = []
    for pat in BANNED_PHRASES:
        m = pat.search(text)
        if m:
            violations.append(f"Banned phrase detected: '{m.group(0)}'")
    return violations


def enforce_safety(reply: str) -> str:
    """Raise ``ValueError`` on critical violations; return text unchanged otherwise."""
    violations = check_safety_violations(reply)
    if violations:
        raise ValueError(
            "Customer reply failed safety check: " + "; ".join(violations)
        )
    return reply