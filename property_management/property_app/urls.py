from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, UnitViewSet, TenantViewSet, LeaseViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'units', UnitViewSet)
router.register(r'tenants', TenantViewSet)
router.register(r'leases', LeaseViewSet)

urlpatterns = router.urls + [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
