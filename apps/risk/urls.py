from django.urls import path
from .views import (
    RiskRuleListView, RiskRuleDetailView,
    RiskEventListView, BlacklistListView, BlacklistDetailView,
)

urlpatterns = [
    path("risk/rules/", RiskRuleListView.as_view(), name="risk-rule-list"),
    path("risk/rules/<uuid:uuid>/", RiskRuleDetailView.as_view(), name="risk-rule-detail"),
    path("risk/events/", RiskEventListView.as_view(), name="risk-event-list"),
    path("risk/blacklist/", BlacklistListView.as_view(), name="blacklist-list"),
    path("risk/blacklist/<uuid:uuid>/", BlacklistDetailView.as_view(), name="blacklist-detail"),
]
