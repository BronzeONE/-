from django.urls import path

from .views import (
    OrderDecisionView,
    PendingCreatingOrdersView,
    PurchaseListView,
    TestReportView,
    TestReportCreateView,
)

urlpatterns = [
    path('creating/', PendingCreatingOrdersView.as_view(), name='orders-creating'),
    path('creating/<int:pk>/decision/', OrderDecisionView.as_view(), name='orders-decision'),
    path('purchases/', PurchaseListView.as_view(), name='orders-purchases'),
    path('purchases/<int:purchase_id>/report/', TestReportView.as_view(), name='test-report-detail'),
    path('reports/', TestReportCreateView.as_view(), name='test-report-create'),
]

