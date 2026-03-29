from django.urls import path
from .views import (
    SessionView,
    CompleteSessionView,
    CompletePageView,
    DashboardView,
)

urlpatterns = [
    path("session/", SessionView.as_view(), name="session"),
    path("session/complete/", CompleteSessionView.as_view(), name="session-complete"),
    path("pages/<int:page_id>/complete/", CompletePageView.as_view(), name="page-complete"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]