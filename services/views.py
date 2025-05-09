from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import Company, Customer, User
from .models import Service, ServiceRequest
from .forms import CreateNewService, RequestServiceForm


def service_list(request):
    """
    Display a list of all services, ordered by most recent first.
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Rendered template with services queryset
    """
    services = Service.objects.all().order_by("-date")
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    """
    Display detailed view of a single service.
    
    Args:
        request: HttpRequest object
        id: Primary key of the Service to display
    
    Returns:
        HttpResponse: Rendered template with service details
    """
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})


def create(request):
    """
    Handle service creation form for companies.
    
    Performs authentication checks and processes form submission.
    Field choices are dynamically determined based on company type.
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Rendered form or redirect on success
    """
    # Authentication and authorization checks
    if not request.user.is_authenticated or not request.user.is_company:
        messages.error(request, "Only companies can create services")
        return redirect('services_list')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        messages.error(request, "Company profile not found")
        return redirect('services_list')

    # Determine available service categories based on company type
    if company.is_all_in_one or company.field == 'All in One':
        choices = Service.choices  # All categories available
    else:
        choices = [(company.field, company.field)]  # Only company's specific field

    if request.method == 'POST':
        form = CreateNewService(request.POST, choices=choices)
        if form.is_valid():
            # Create and save new service
            service = Service(
                company=company,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                price_hour=form.cleaned_data['price_hour'],
                field=form.cleaned_data['field']
            )
            service.save()
            messages.success(request, f"Service '{service.name}' created successfully")
            return redirect('services_list')
    else:
        form = CreateNewService(choices=choices)
    
    return render(request, 'services/create.html', {'form': form})


def service_field(request, field):
    """
    Display services filtered by a specific category/field.
    
    Args:
        request: HttpRequest object
        field: Service category (URL parameter, hyphens converted to spaces)
    
    Returns:
        HttpResponse: Rendered template with filtered services
    """
    # Convert URL-friendly field name to display format
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(field=field)
    return render(request, 'services/field.html', {'services': services, 'field': field})


def request_service(request, id):
    """
    Handle service request submission from customers.
    
    Performs authentication checks, processes form submission,
    and calculates total price based on service rate and hours.
    
    Args:
        request: HttpRequest object
        id: Primary key of the requested Service
    
    Returns:
        HttpResponse: Rendered form or redirect on success
    """
    # Authentication and authorization checks
    if not request.user.is_authenticated or not request.user.is_customer:
        messages.error(request, "Only customers can request services")
        return redirect('services_list')
    
    try:
        service = Service.objects.get(id=id)
        customer = Customer.objects.get(user=request.user)
    except Service.DoesNotExist:
        messages.error(request, "Service not found")
        return redirect('services_list')
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found")
        return redirect('services_list')
    
    if request.method == 'POST':
        form = RequestServiceForm(request.POST)
        if form.is_valid():
            # Extract cleaned form data
            hours = form.cleaned_data['hours']
            location = form.cleaned_data['location']
            additional_notes = form.cleaned_data.get('additional_notes', '')
            
            # Calculate total price
            price = service.price_hour * hours
            
            # Create and save service request
            service_request = ServiceRequest(
                customer=customer,
                service=service,
                hours=hours,
                location=location,
                price=price,
                additional_notes=additional_notes,
            )
            service_request.save()
            
            # Detailed success message with pricing breakdown
            messages.success(
                request, 
                f"Service request for '{service.name}' submitted successfully. "
                f"Total cost: {price}€ ({service.price_hour}€/hour × {hours} hours)"
            )
            return redirect('customer_profile', name=request.user.username)
    else:
        form = RequestServiceForm()
    
    context = {
        'service': service,
        'form': form,
    }
    return render(request, 'services/request_service.html', context)