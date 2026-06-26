"""HTTP views for QueueStorm — both the JSON API and the server-rendered UI."""

from __future__ import annotations

import logging

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket, TicketAnalysis
from .serializers import TicketInputSerializer
from engine import analyzer
from engine.safety import detect_injection


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public JSON API
# ---------------------------------------------------------------------------


@api_view(['GET'])
def health(request):
    """GET /health — judges check service readiness with this endpoint."""
    return Response({"status": "ok"})


class AnalyzeTicketView(APIView):
    """POST /analyze-ticket — main analysis endpoint.

    Accepts a ticket payload, validates it, runs the rule-based engine,
    persists the result, and returns the structured JSON response exactly
    matching the spec.
    """

    def post(self, request):
        # 1. Schema validation — return 400 on malformed JSON / missing required fields.
        serializer = TicketInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = dict(serializer.validated_data)

        # 2. Semantic validation — empty complaint string is 422.
        if not data.get('complaint', '').strip():
            return Response(
                {"error": "Complaint cannot be empty."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # 3. Prompt injection detection — log and tag, do not stop analysis.
        injection_detected = detect_injection(data['complaint'])
        if injection_detected:
            logger.warning(
                "Possible prompt-injection attempt in ticket %s",
                data.get('ticket_id'),
            )

        # 4. Run the rule-based engine.
        try:
            result = analyzer.analyze(data)
        except Exception:
            # Never expose stack traces or secrets in the response body.
            logger.exception("Engine failed for ticket %s", data.get('ticket_id'))
            return Response(
                {"error": "Analysis failed. Please retry."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 5. Persist for the dashboard / ticket history UI.
        try:
            self._persist(data, result, injection_detected)
        except Exception:
            logger.exception("Persistence failed for ticket %s", data.get('ticket_id'))
            # Persistence failure must not break the public API contract.
            # Continue and return the analysis result anyway.

        if injection_detected:
            codes = result.setdefault('reason_codes', [])
            if 'prompt_injection_attempt' not in codes:
                codes.append('prompt_injection_attempt')

        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    def _persist(data: dict, result: dict, injection_detected: bool) -> None:
        ticket, _ = Ticket.objects.update_or_create(
            ticket_id=data['ticket_id'],
            defaults={
                'complaint': data['complaint'],
                'language': data.get('language') or 'en',
                'channel': data.get('channel') or '',
                'user_type': data.get('user_type') or 'unknown',
                'campaign_context': data.get('campaign_context') or '',
                'metadata': data.get('metadata') or {},
            },
        )

        # Replace the transaction history snapshot to keep DB state coherent.
        ticket.transaction_history.all().delete()
        for tx in data.get('transaction_history', []) or []:
            ticket.transaction_history.create(
                transaction_id=tx['transaction_id'],
                timestamp=tx['timestamp'],
                type=tx['type'],
                amount=tx['amount'],
                counterparty=tx.get('counterparty', '') or '',
                status=tx['status'],
            )

        TicketAnalysis.objects.update_or_create(
            ticket=ticket,
            defaults={
                'relevant_transaction_id': result.get('relevant_transaction_id'),
                'evidence_verdict': result['evidence_verdict'],
                'case_type': result['case_type'],
                'severity': result['severity'],
                'department': result['department'],
                'agent_summary': result['agent_summary'],
                'recommended_next_action': result['recommended_next_action'],
                'customer_reply': result['customer_reply'],
                'human_review_required': result['human_review_required'],
                'confidence': result.get('confidence'),
                'reason_codes': result.get('reason_codes', []),
                'injection_detected': injection_detected,
                'analyzed_at': timezone.now(),
            },
        )


# ---------------------------------------------------------------------------
# Server-rendered UI
# ---------------------------------------------------------------------------


def dashboard(request):
    """Home page: hero + live stats."""
    total = Ticket.objects.count()
    pending_review = Ticket.objects.filter(
        analysis__human_review_required=True
    ).distinct().count()
    today = Ticket.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    critical = Ticket.objects.filter(analysis__severity='critical').count()

    ctx = {
        'total': total,
        'pending_review': pending_review,
        'today': today,
        'critical': critical,
    }
    return render(request, 'core/dashboard.html', ctx)


def submit(request):
    """Form page for submitting a single ticket."""
    return render(request, 'core/submit.html', {})


def ticket_list(request):
    """Paginated, filterable ticket history."""
    qs = Ticket.objects.select_related('analysis').order_by('-created_at')

    # Simple filter plumbing — keeps the UI useful without dragging in JS.
    severity = request.GET.get('severity', '').strip()
    case_type = request.GET.get('case_type', '').strip()
    department = request.GET.get('department', '').strip()
    needs_review = request.GET.get('human_review_required', '').strip()

    if severity:
        qs = qs.filter(analysis__severity=severity)
    if case_type:
        qs = qs.filter(analysis__case_type=case_type)
    if department:
        qs = qs.filter(analysis__department=department)
    if needs_review == '1':
        qs = qs.filter(analysis__human_review_required=True)
    elif needs_review == '0':
        qs = qs.filter(analysis__human_review_required=False)

    page_size = 25
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except ValueError:
        page = 1
    start = (page - 1) * page_size
    end = start + page_size
    items = list(qs[start:end])
    has_next = qs.count() > end

    ctx = {
        'items': items,
        'page': page,
        'has_prev': page > 1,
        'has_next': has_next,
        'severity': severity,
        'case_type': case_type,
        'department': department,
        'needs_review': needs_review,
        'filter_qs': request.GET.urlencode(),
    }
    return render(request, 'core/ticket_list.html', ctx)


def ticket_detail(request, ticket_id: str):
    """Detail page for one ticket — input on the left, analysis on the right."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    analysis = getattr(ticket, 'analysis', None)
    transactions = list(
        ticket.transaction_history.all().order_by('timestamp').values(
            'transaction_id', 'timestamp', 'type', 'amount',
            'counterparty', 'status',
        )
    )
    ctx = {
        'ticket': ticket,
        'analysis': analysis,
        'transactions': transactions,
    }
    return render(request, 'core/ticket_detail.html', ctx)


def api_docs(request):
    """Plain-text API reference page."""
    return render(request, 'core/api_docs.html', {})
