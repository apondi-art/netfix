from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from users.models import Company, Customer, User
from .models import Service,ServiceRequest
from .forms import CreateNewService, RequestServiceForm


def service_list(request):
    services = Service.objects.all().order_by("-date")
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})

def create(request):
    # First check authentication and company status
    if not request.user.is_authenticated or not request.user.is_company:
        messages.error(request, "Only companies can create services")
        return redirect('services_list')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        messages.error(request, "Company profile not found")
        return redirect('services_list')

    # Determine choices based on company type
    if company.is_all_in_one or company.field == 'All in One':
        choices = Service.choices
    else:
        choices = [(company.field, company.field)]

    if request.method == 'POST':
        form = CreateNewService(request.POST, choices=choices)
        if form.is_valid():
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
    # search for the service present in the url
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(
        field=field)
    return render(request, 'services/field.html', {'services': services, 'field': field})

def request_service(request, id):
    # Check if user is authenticated and is a customer
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
            hours = form.cleaned_data['hours']
            location = form.cleaned_data['location']
            additional_notes = form.cleaned_data.get('additional_notes', '')
            
            # Calculate price based on service hourly rate and hours requested
            price = service.price_hour * hours
            
            # Create service request
            service_request = ServiceRequest(
                customer=customer,
                service=service,
                hours=hours,
                location=location,
                price=price,
                additional_notes=additional_notes,
            )
            service_request.save()
            
            # Display more detailed success message including price
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