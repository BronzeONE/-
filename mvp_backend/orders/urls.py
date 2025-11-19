from django.urls import path

from .views import OrderDecisionView, PendingCreatingOrdersView, PurchaseListView

urlpatterns = [
    path('creating/', PendingCreatingOrdersView.as_view(), name='orders-creating'),
    path('creating/<int:pk>/decision/', OrderDecisionView.as_view(), name='orders-decision'),
    path('purchases/', PurchaseListView.as_view(), name='orders-purchases'),
]

