from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.db.models import Count
from services.models import Service, ServiceRequest

def home(request):
    # Get the 5 most requested services by counting ServiceRequest entries
    most_requested_services = Service.objects.annotate(
        request_count=Count('requests')  
    ).order_by('-request_count')[:5]
    
    context = {
        'most_requested_services': most_requested_services
    }
    return render(request, "main/home.html", context)

def logout(request):
    django_logout(request)
    return render(request, "main/logout.html")