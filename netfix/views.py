from django.shortcuts import render,redirect
from django.contrib import messages
from users.models import User, Company,Customer
from services.models import Service,ServiceRequest


def home(request):
    return render(request, 'users/home.html', {'user': request.user})


def customer_profile(request, name):
    # Fetch the customer user and all of the service requests
    try:
        user = User.objects.get(username=name)
        if not user.is_customer:
            messages.error(request, "This user is not a customer")
            return redirect('home')
            
        customer = Customer.objects.get(user=user)
        service_history = ServiceRequest.objects.filter(customer=customer).order_by("-request_date")
        
        # Calculate user age (if you have a date_of_birth field in your Customer model)
        user_age = None
        if hasattr(customer, 'date_of_birth'):
            from datetime import date
            today = date.today()
            born = customer.date_of_birth
            user_age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        
        context = {
            'user': user,
            'user_age': user_age,
            'sh': service_history,  # Using 'sh' to match your template
        }
        
        return render(request, 'users/profile.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('home')
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found")
        return redirect('home')


def company_profile(request, name):
    # fetches the company user and all of the services available by it
    user = User.objects.get(username=name)
    services = Service.objects.filter(
        company=Company.objects.get(user=user)).order_by("-date")

    return render(request, 'users/profile.html', {'user': user, 'services': services})
