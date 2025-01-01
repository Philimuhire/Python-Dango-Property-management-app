from django.urls import path
from .views import (
    PropertyListView, PropertyDetailView,
    AdminDashboardView, LandlordDashboardView, TenantDashboardView
)

urlpatterns = [
    path('', PropertyListView.as_view(), name='property_list'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/landlord/', LandlordDashboardView.as_view(), name='landlord_dashboard'),
    path('dashboard/tenant/', TenantDashboardView.as_view(), name='tenant_dashboard'),
]

