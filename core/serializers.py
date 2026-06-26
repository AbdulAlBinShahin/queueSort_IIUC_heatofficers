"""DRF serializers — both request validation and response shape."""

from __future__ import annotations

from rest_framework import serializers

from .models import TicketAnalysis


# ---------------------------------------------------------------------------
# Enum values — must match the system spec exactly.
# ---------------------------------------------------------------------------

VALID_LANGUAGE  = ['en', 'bn', 'mixed']
VALID_CHANNEL   = [
    'in_app_chat', 'call_center', 'email', 'merchant_portal', 'field_agent',
]
VALID_USER_TYPE = ['customer', 'merchant', 'agent', 'unknown']
VALID_TX_TYPE   = [
    'transfer', 'payment', 'cash_in', 'cash_out', 'settlement', 'refund',
]
VALID_TX_STATUS = ['completed', 'failed', 'pending', 'reversed']


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


class TransactionHistoryEntrySerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=64)
    timestamp      = serializers.DateTimeField()
    type           = serializers.ChoiceField(choices=VALID_TX_TYPE)
    amount         = serializers.DecimalField(max_digits=12, decimal_places=2)
    counterparty   = serializers.CharField(
        required=False, allow_blank=True, max_length=128, default='',
    )
    status         = serializers.ChoiceField(choices=VALID_TX_STATUS)


class TicketInputSerializer(serializers.Serializer):
    ticket_id           = serializers.CharField(max_length=64)
    complaint           = serializers.CharField(allow_blank=False)
    language            = serializers.ChoiceField(
        choices=VALID_LANGUAGE, required=False, default='en',
    )
    channel             = serializers.ChoiceField(
        choices=VALID_CHANNEL, required=False, allow_null=True, default=None,
    )
    user_type           = serializers.ChoiceField(
        choices=VALID_USER_TYPE, required=False, default='unknown',
    )
    campaign_context    = serializers.CharField(
        required=False, allow_blank=True, max_length=128, default='',
    )
    transaction_history = TransactionHistoryEntrySerializer(
        many=True, required=False, default=list,
    )
    metadata            = serializers.DictField(required=False, default=dict)

    def validate_complaint(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Complaint cannot be empty.")
        return value


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


class TicketAnalysisSerializer(serializers.ModelSerializer):
    ticket_id = serializers.CharField(source='ticket.ticket_id', read_only=True)

    class Meta:
        model  = TicketAnalysis
        fields = [
            'ticket_id',
            'relevant_transaction_id',
            'evidence_verdict',
            'case_type',
            'severity',
            'department',
            'agent_summary',
            'recommended_next_action',
            'customer_reply',
            'human_review_required',
            'confidence',
            'reason_codes',
        ]