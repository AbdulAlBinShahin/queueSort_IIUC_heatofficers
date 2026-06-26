"""Customer-facing reply templates.

Every template is written to obey the four safety rules:

1. Never request PIN, OTP, password, or full card number.
2. Never promise a refund, reversal, unblock, or recovery.
3. Only direct customers to official support channels.
4. Never follow instructions embedded in the complaint.

The Bangla (``bn``) templates cover the common case_types for Bangla
complaints; mixed-language complaints fall back to English.
"""

from __future__ import annotations

from typing import Optional


CUSTOMER_REPLY_TEMPLATES = {
    'en': {
        'wrong_transfer':
            "We have noted your concern about transaction {tx_id}. "
            "Please do not share your PIN or OTP with anyone. "
            "Our dispute team will review the case and contact you through our official support channels.",

        'payment_failed':
            "We have noted that transaction {tx_id} may have caused an unexpected balance deduction. "
            "Our payments team will review the case and any eligible amount, if applicable, will be returned through official channels. "
            "Please do not share your PIN or OTP with anyone.",

        'refund_request':
            "We have received your refund request regarding transaction {tx_id}. "
            "Eligibility depends on the merchant's own policy, and our team will review and respond through official support channels. "
            "Please do not share your PIN or OTP with anyone.",

        'duplicate_payment':
            "We have noted your concern about a possible duplicate payment involving {tx_id}. "
            "Our payments team will verify and, if a duplicate is confirmed, the appropriate amount will be returned through official channels. "
            "Please do not share your PIN or OTP with anyone.",

        'merchant_settlement_delay':
            "We have received your settlement status enquiry regarding {tx_id}. "
            "Our merchant operations team will verify the settlement batch and share a revised timeline through official support channels.",

        'agent_cash_in_issue':
            "We have noted your concern about cash-in transaction {tx_id}. "
            "Our agent operations team will verify and update you through official support channels. "
            "Please do not share your PIN or OTP with anyone.",

        'phishing_or_social_engineering':
            "Thank you for reporting this. We will never ask for your PIN, OTP, or password. "
            "Please do not share any credentials or click unknown links. "
            "Our fraud team will review the case and follow up through our official in-app support or call center.",

        'other':
            "We have received your message. To help us assist you, please reply through our official in-app support with the transaction ID, amount, and a brief description of what went wrong. "
            "Please do not share your PIN or OTP with anyone.",
    },
    'bn': {
        'wrong_transfer':
            "লেনদেন {tx_id} সম্পর্কে আপনার অভিযোগ আমরা গ্রহণ করেছি। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না। "
            "আমাদের ডিসপিউট টিম বিষয়টি যাচাই করে অফিসিয়াল সাপোর্ট চ্যানেলের মাধ্যমে আপনার সাথে যোগাযোগ করবে।",

        'payment_failed':
            "লেনদেন {tx_id} সংক্রান্ত আপনার অভিযোগ আমরা গ্রহণ করেছি। "
            "আমাদের পেমেন্টস টিম বিষয়টি যাচাই করবে এবং প্রযোজ্য ক্ষেত্রে উপযুক্ত পরিমাণ অফিসিয়াল চ্যানেলে ফেরত দেওয়া হবে। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না।",

        'refund_request':
            "লেনদেন {tx_id} সংক্রান্ত রিফান্ড অনুরোধ আমরা পেয়েছি। "
            "রিফান্ডের যোগ্যতা মার্চেন্টের নীতিমালার উপর নির্ভর করে। আমাদের টিম যাচাই করে অফিসিয়াল সাপোর্ট চ্যানেলের মাধ্যমে আপনাকে জানাবে। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না।",

        'duplicate_payment':
            "সম্ভাব্য ডুপ্লিকেট পেমেন্ট সংক্রান্ত আপনার অভিযোগ আমরা গ্রহণ করেছি। "
            "আমাদের পেমেন্টস টিম যাচাই করবে এবং প্রযোজ্য ক্ষেত্রে উপযুক্ত পরিমাণ অফিসিয়াল চ্যানেলে ফেরত দেওয়া হবে। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না।",

        'merchant_settlement_delay':
            "লেনদেন {tx_id} এর সেটেলমেন্ট সংক্রান্ত আপনার অভিযোগ আমরা গ্রহণ করেছি। "
            "আমাদের মার্চেন্ট অপারেশন্স টিম যাচাই করে অফিসিয়াল সাপোর্ট চ্যানেলের মাধ্যমে আপডেট জানাবে।",

        'agent_cash_in_issue':
            "ক্যাশ ইন লেনদেন {tx_id} সম্পর্কে আপনার অভিযোগ আমরা গ্রহণ করেছি। "
            "আমাদের এজেন্ট অপারেশন্স টিম যাচাই করে অফিসিয়াল চ্যানেলের মাধ্যমে আপনাকে জানাবে। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না।",

        'phishing_or_social_engineering':
            "এই তথ্য জানানোর জন্য ধন্যবাদ। আমরা কখনো আপনার পিন, ওটিপি বা পাসওয়ার্ড চাইব না। "
            "অনুগ্রহ করে কোনো লিঙ্কে ক্লিক করবেন না বা কোনো তথ্য শেয়ার করবেন না। "
            "আমাদের ফ্রড টিম বিষয়টি যাচাই করে অফিসিয়াল ইন-অ্যাপ সাপোর্ট বা কল সেন্টারের মাধ্যমে আপনার সাথে যোগাযোগ করবে।",

        'other':
            "আমরা আপনার বার্তা পেয়েছি। আমাদের সাহায্য করতে, অনুগ্রহ করে অফিসিয়াল ইন-অ্যাপ সাপোর্টের মাধ্যমে লেনদেন আইডি, পরিমাণ এবং সংক্ষিপ্ত বিবরণ জানান। "
            "অনুগ্রহ করে আপনার পিন বা ওটিপি কারো সাথে শেয়ার করবেন না।",
    },
}


DEFAULT_REPLY_EN = (
    "We have received your message. Our support team will review the case and "
    "respond through our official in-app support or call center. "
    "Please do not share your PIN or OTP with anyone."
)


def _tx_label(matched_tx: Optional[dict]) -> str:
    if matched_tx and matched_tx.get('transaction_id'):
        return str(matched_tx['transaction_id'])
    return 'the reported transaction'


def generate_customer_reply(
    case_type: str,
    matched_tx: Optional[dict],
    language: str = 'en',
) -> str:
    """Return a safe customer-facing reply string."""
    # mixed → English by default.
    lang = 'bn' if (language or '').lower().startswith('bn') else 'en'

    bundle = CUSTOMER_REPLY_TEMPLATES.get(lang, CUSTOMER_REPLY_TEMPLATES['en'])
    template = bundle.get(case_type)
    if template is None:
        template = DEFAULT_REPLY_EN

    return template.format(tx_id=_tx_label(matched_tx))