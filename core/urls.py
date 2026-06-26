"""URL routing for the server-rendered UI."""

from django.urls import path

from . import views


app_name = 'core'

urlpatterns = [
    path('',                        views.dashboard,     name='dashboard'),
    path('submit/',                 views.submit,        name='submit'),
    path('tickets/',                views.ticket_list,   name='ticket-list'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket-detail'),
    path('docs/',                   views.api_docs,      name='api-docs'),
]