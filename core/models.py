"""Persistent models — every input ticket and its analysis result."""

from django.db import models


class Ticket(models.Model):
    """A single support ticket, as received from the judge harness or UI."""

    ticket_id          = models.CharField(max_length=64, unique=True)
    complaint          = models.TextField()
    language           = models.CharField(max_length=8,  blank=True, default='en')
    channel            = models.CharField(max_length=32, blank=True, default='')
    user_type          = models.CharField(max_length=16, blank=True, default='unknown')
    campaign_context   = models.CharField(max_length=128, blank=True, default='')
    metadata           = models.JSONField(default=dict, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.ticket_id


class TransactionHistoryEntry(models.Model):
    """A single transaction associated with a ticket."""

    ticket         = models.ForeignKey(
        Ticket, related_name='transaction_history', on_delete=models.CASCADE
    )
    transaction_id = models.CharField(max_length=64)
    timestamp      = models.DateTimeField()
    type           = models.CharField(max_length=32)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    counterparty   = models.CharField(max_length=128, blank=True, default='')
    status         = models.CharField(max_length=16)

    class Meta:
        ordering = ['timestamp']

    def __str__(self) -> str:
        return f"{self.transaction_id} ({self.type}, {self.amount})"


class TicketAnalysis(models.Model):
    """Engine output for one ticket — written once, read many."""

    ticket                   = models.OneToOneField(
        Ticket, related_name='analysis', on_delete=models.CASCADE
    )
    relevant_transaction_id  = models.CharField(max_length=64, null=True, blank=True)
    evidence_verdict         = models.CharField(max_length=24)
    case_type                = models.CharField(max_length=48)
    severity                 = models.CharField(max_length=16)
    department               = models.CharField(max_length=32)
    agent_summary            = models.TextField()
    recommended_next_action  = models.TextField()
    customer_reply           = models.TextField()
    human_review_required    = models.BooleanField(default=True)
    confidence               = models.FloatField(null=True, blank=True)
    reason_codes             = models.JSONField(default=list, blank=True)
    injection_detected       = models.BooleanField(default=False)
    analyzed_at              = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.ticket.ticket_id} → {self.case_type} / {self.severity}"
