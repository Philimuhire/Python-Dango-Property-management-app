from rest_framework import viewsets
from .models import Property, Unit, Tenant, Lease, PropertyImage
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

@method_decorator(login_required, name='dispatch')
class LandlordDashboardView(TemplateView):
    template_name = 'property_app/landlord_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'landlord':
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TenantDashboardView(TemplateView):
    template_name = 'property_app/tenant_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'tenant':
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)