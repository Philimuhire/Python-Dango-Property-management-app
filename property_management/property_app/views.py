from rest_framework import viewsets
from .models import Property, Unit, Tenant, Lease, PropertyImage, MaintenanceRequest
from .serializers import PropertySerializer, UnitSerializer, TenantSerializer, LeaseSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from .forms import PropertyImageForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Avg, Sum
from django.http import HttpResponseForbidden
from .forms import MaintenanceRequestForm
from django.http import HttpResponseRedirect

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]

class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer
    permission_classes = [IsAuthenticated]
    

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            user.profile.role = role
            user.profile.save()
            login(request, user)
            return redirect('property_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})

class PropertyListView(ListView):
    model = Property
    template_name = 'property_app/property_list.html'
    context_object_name = 'properties'

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_app/property_detail.html'
    context_object_name = 'property'
    
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_app/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = PropertyImageForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != 'landlord':
            return redirect('login')
        
        self.object = self.get_object()
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            property_image = form.save(commit=False)
            property_image.property = self.object
            property_image.save()
            return redirect('property_detail', pk=self.object.pk)
        context = self.get_context_data()
        context['image_form'] = form
        return self.render_to_response(context)
    
class PropertyListView(ListView):
    model = Property
    template_name = 'property_app/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10  # Optional: Add pagination

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        property_type = self.request.GET.get('property_type')
        min_units = self.request.GET.get('min_units')
        max_units = self.request.GET.get('max_units')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(description__icontains=query)
            )
        if property_type and property_type != 'All':
            queryset = queryset.filter(property_type=property_type)
        if min_units:
            queryset = queryset.filter(number_of_units__gte=min_units)
        if max_units:
            queryset = queryset.filter(number_of_units__lte=max_units)
        return queryset

@method_decorator(login_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'property_app/admin_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate metrics
        total_properties = Property.objects.count()
        total_units = Unit.objects.count()
        total_tenants = Tenant.objects.count()
        total_leases = Lease.objects.count()
        occupancy_rate = (total_units and (total_leases / total_units) * 100) or 0
        
        # Sum up the rent amounts
        total_revenue = Lease.objects.aggregate(Sum('rent_amount'))['rent_amount__sum'] or 0
        
        # Add metrics to context
        context.update({
            'total_properties': total_properties,
            'total_units': total_units,
            'total_tenants': total_tenants,
            'total_leases': total_leases,
            'occupancy_rate': round(occupancy_rate, 2),
            'total_revenue': total_revenue,
        })
        return context

@method_decorator(login_required, name='dispatch')
class LandlordDashboardView(TemplateView):
    template_name = 'property_app/landlord_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'landlord':
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the landlord's properties
        landlord_properties = Property.objects.filter(owner=self.request.user)

        # Fetch maintenance requests related to the landlord's properties
        maintenance_requests = MaintenanceRequest.objects.filter(property__in=landlord_properties)

        # Pass properties and maintenance requests to the template
        context['properties'] = landlord_properties
        context['maintenance_requests'] = maintenance_requests

        return context

@method_decorator(login_required, name='dispatch')
class TenantDashboardView(TemplateView):
    template_name = 'property_app/tenant_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'tenant':
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def submit_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.tenant = request.user
            maintenance_request.save()
            return redirect('request_list')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'maintenance/submit_request.html', {'form': form})

@login_required
def request_list(request):
    if request.user.is_staff:  # Assuming staff users manage requests
        requests = MaintenanceRequest.objects.all()
    else:
        requests = MaintenanceRequest.objects.filter(tenant=request.user)

    return render(request, 'maintenance/request_list.html', {'requests': requests})

@login_required
def update_request_status(request, pk, status):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    maintenance_request.status = status
    maintenance_request.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class MyRequestsView(ListView):
    template_name = 'maintenance/my_requests.html'  # Create this template
    context_object_name = 'requests'

    def get_queryset(self):
        # Filter requests for the logged-in tenant
        return MaintenanceRequest.objects.filter(tenant=self.request.user)