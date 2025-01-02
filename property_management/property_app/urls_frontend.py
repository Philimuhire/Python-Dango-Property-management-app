from django.urls import path
from . import views
from .views import (
    PropertyListView, PropertyDetailView,
    AdminDashboardView, LandlordDashboardView, TenantDashboardView,
)

urlpatterns = [
    path('', PropertyListView.as_view(), name='property_list'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/landlord/', LandlordDashboardView.as_view(), name='landlord_dashboard'),
    path('dashboard/tenant/', TenantDashboardView.as_view(), name='tenant_dashboard'),
    path('submit/', views.submit_request, name='submit_request'),
    path('list/', views.request_list, name='request_list'),
    path('update/<int:pk>/<str:status>/', views.update_request_status, name='update_request_status'),
     path('maintenance/requests/', views.MyRequestsView.as_view(), name='my_requests'),
]

