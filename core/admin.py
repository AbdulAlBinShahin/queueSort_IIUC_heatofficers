"""Django admin registration — convenience for inspecting submitted tickets."""

from django.contrib import admin

from .models import Ticket, TransactionHistoryEntry, TicketAnalysis


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'language', 'channel', 'user_type', 'created_at')
    search_fields = ('ticket_id', 'complaint')


@admin.register(TransactionHistoryEntry)
class TransactionHistoryEntryAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'type', 'amount', 'status', 'timestamp', 'ticket')
    search_fields = ('transaction_id', 'counterparty')


@admin.register(TicketAnalysis)
class TicketAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'ticket', 'case_type', 'severity', 'department',
        'human_review_required', 'analyzed_at',
    )
    list_filter = ('case_type', 'severity', 'department', 'human_review_required')
    search_fields = ('ticket__ticket_id',)
