"""URL Configuration for the QueueStorm Investigator service."""

from django.contrib import admin
from django.urls import path, include

from core.views import health, AnalyzeTicketView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Public API endpoints used by the judge harness.
    path('health',          health,                  name='health'),
    path('analyze-ticket',  AnalyzeTicketView.as_view(), name='analyze-ticket'),

    # Server-rendered UI (dashboard, submit, list, detail).
    path('', include('core.urls')),
]
