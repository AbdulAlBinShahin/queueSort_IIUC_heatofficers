"""Keyword sets (English + Bangla + Banglish) used by the rule engine.

These are intentionally conservative — only clear signals are matched.
"""

# ---------------------------------------------------------------------------
# Phishing / social engineering — always highest priority.
# ---------------------------------------------------------------------------

PHISHING_EN = [
    "otp", "pin", "password", "cvv", "one time password",
    "asked for my pin", "asked for my otp", "asked for my password",
    "asked me for", "asked me to share", "share my pin", "share my otp",
    "share otp", "share pin", "share password",
    "someone called", "called me", "fake call", "fake sms", "fake message",
    "phishing", "scammer", "fraud call", "fraud sms",
    "verify my account", "verify your account",
    "click this link", "click the link", "send me a code",
    "impersonator", "pretended to be", "asked for otp", "asked for pin",
    "received a call", "received an sms",
]

PHISHING_BN = [
    "ওটিপি", "ও.টি.পি", "পিন", "পাসওয়ার্ড", "পাসওয়ার্ড দিয়েছি",
    "কেউ কল করেছিল", "কেউ ফোন করেছিল", "কল করেছিল",
    "কেউ এসএমএস", "ভুয়া এসএমএস", "ভুয়া কল",
    "টাকা চেয়েছে", "পিন চেয়েছে", "ওটিপি চেয়েছে",
    "আমার পিন", "আমার ওটিপি",
]

PHISHING_BANGLISH = [
    "otp dao", "pin dao", "pin den", "otp den",
    "keu call korlo", "keu call koreche",
    "fake call", "fake sms",
    "amar pin", "amar otp",
    "password chais", "pin chais", "otp chais",
    "scammer call", "scam call", "scam sms",
]


# ---------------------------------------------------------------------------
# Cash-in via agent
# ---------------------------------------------------------------------------

AGENT_CASH_IN_EN = [
    "cash in", "cash-in", "cashin", "deposit through agent", "deposited through",
    "agent didn't", "agent did not", "agent gave less", "agent didn't give",
    "agent number", "agent hasn't", "agent has not",
    "not reflected", "didn't receive", "did not receive",
    "balance not updated", "balance not credited", "not credited",
    "amount not added", "money not added",
]

AGENT_CASH_IN_BN = ["ক্যাশ ইন", "এজেন্ট", "জমা", "ব্যালেন্স আসেনি", "টাকা আসেনি"]
AGENT_CASH_IN_BANGLISH = [
    "agent", "cash in", "cash-in", "deposit",
    "balance eshe nai", "balance asheni", "taka asheni",
    "agent taka diye nai", "agent taka diyeni",
]


# ---------------------------------------------------------------------------
# Merchant settlement delay
# ---------------------------------------------------------------------------

MERCHANT_SETTLEMENT_EN = [
    "settlement", "settle", "settled", "payout",
    "merchant", "merchant account", "settlement delay", "settlement not",
    "money not settled", "settlement not received", "not settled yet",
    "weekly settlement", "daily settlement", "merchant portal",
]

MERCHANT_SETTLEMENT_BANGLISH = [
    "settlement", "settle hoyni", "settle hoy nai",
    "merchant", "payout delay", "payout hoyni",
]


# ---------------------------------------------------------------------------
# Duplicate payment
# ---------------------------------------------------------------------------

DUPLICATE_EN = [
    "twice", "two times", "two times charged", "two times deducted",
    "charged twice", "deducted twice", "double charged", "double payment",
    "duplicate", "same payment twice", "same amount twice",
    "two times bill", "two bills",
]
DUPLICATE_BANGLISH = [
    "duibar", "doibar", "two times", "twice",
    "double charge", "duplicate payment",
]


# ---------------------------------------------------------------------------
# Payment failed (balance deducted)
# ---------------------------------------------------------------------------

PAYMENT_FAILED_EN = [
    "payment failed", "transaction failed", "failed but",
    "deducted but", "balance deducted but", "money deducted but",
    "amount deducted but", "payment unsuccessful", "transaction unsuccessful",
    "not successful", "didn't go through", "did not go through",
    "didn't work", "did not work",
    "but i didn't receive", "but i did not receive",
    "money was taken", "amount was taken", "but payment failed",
    "balance cut but", "balance deducted however",
]
PAYMENT_FAILED_BN = ["ব্যর্থ", "হয়নি", "পাইনি", "কাটা হয়েছে", "কেটে নিয়েছে", "কেটে নিয়েছে কিন্তু"]
PAYMENT_FAILED_BANGLISH = [
    "fail hoyeche", "fail hoy nai", "vangh hoyeche",
    "kete niyese", "kete niyeche", "kete nise",
    "taka kete niyeche", "balance kete geche",
    "but pai nai", "taka pai nai",
    "transaction hoi nai", "payment hoi nai",
]


# ---------------------------------------------------------------------------
# Wrong transfer
# ---------------------------------------------------------------------------

WRONG_TRANSFER_EN = [
    "wrong number", "wrong person", "wrong recipient", "wrong account",
    "wrong phone", "mistakenly sent", "accidentally sent", "by mistake",
    "sent to wrong", "transferred to wrong",
    "typed wrong", "mistyped", "wrong digit",
    "sent it to the wrong", "sent to the wrong",
    "didn't receive", "did not receive", "never received", "not received",
    "hasn't received", "has not received", "no one received",
    "receiver says", "recipient says",
    "please return my money", "please send back", "please refund my money",
]
WRONG_TRANSFER_BN = ["ভুল নম্বর", "ভুল ব্যক্তি", "ভুল প্রাপক", "ভুল করে", "ভুল করে পাঠিয়েছি"]
WRONG_TRANSFER_BANGLISH = [
    "vool number", "vool person", "vool lok", "vul number", "vul person",
    "vul kore", "vool kore", "bhul kore", "bhul number",
    "send back", "ferot", "ferot diyen", "please return",
]


# ---------------------------------------------------------------------------
# Refund request (generic)
# ---------------------------------------------------------------------------

REFUND_EN = [
    "refund", "money back", "give back", "return my money",
    "please refund", "i want refund", "i need refund",
    "want my money back", "need my money back", "want refund",
]
REFUND_BN = ["ফেরত", "রিফান্ড", "টাকা ফেরত", "টাকা ফেরত দিন"]
REFUND_BANGLISH = ["refund", "taka ferot", "ferot din", "taka ferot din"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def any_match(text_lower: str, keyword_list) -> bool:
    """Case-insensitive substring match for short keywords, exact for short ones."""
    for kw in keyword_list:
        kw_l = kw.lower()
        # For very short tokens, require word-boundary-ish matching to avoid noise.
        if len(kw_l) <= 3:
            if f" {kw_l} " in f" {text_lower} ":
                return True
        else:
            if kw_l in text_lower:
                return True
    return False


def all_keyword_groups():
    """Returns the priority-ordered groups used by the classifier."""
    return [
        ('phishing_or_social_engineering', PHISHING_EN + PHISHING_BN + PHISHING_BANGLISH),
        ('agent_cash_in_issue',            AGENT_CASH_IN_EN + AGENT_CASH_IN_BN + AGENT_CASH_IN_BANGLISH),
        ('merchant_settlement_delay',      MERCHANT_SETTLEMENT_EN + MERCHANT_SETTLEMENT_BANGLISH),
        ('duplicate_payment',              DUPLICATE_EN + DUPLICATE_BANGLISH),
        ('payment_failed',                 PAYMENT_FAILED_EN + PAYMENT_FAILED_BN + PAYMENT_FAILED_BANGLISH),
        ('wrong_transfer',                 WRONG_TRANSFER_EN + WRONG_TRANSFER_BN + WRONG_TRANSFER_BANGLISH),
        ('refund_request',                 REFUND_EN + REFUND_BN + REFUND_BANGLISH),
    ]