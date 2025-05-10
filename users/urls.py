from django.urls import path
from django.contrib.auth import views  # Django's built-in auth views

# Import custom form and views
from .forms import UserLoginForm
from . import views as v  # Local views with custom auth logic

urlpatterns = [
    # Registration landing page - directs users to appropriate registration flow
    path('', v.register, name='register'),
    
    # Custom login view using Django's authentication system
    # Uses UserLoginForm for email-based authentication instead of username
    path('login/', v.LoginUserView.as_view(), name='login'),
    
    # Company registration endpoint
    # Uses class-based view for company signup with form processing
    path('company/', v.CompanySignUpView.as_view(), name='register_company'),
    
    # Customer registration endpoint  
    # Uses class-based view for customer signup with additional profile data
    path('customer/', v.CustomerSignUpView.as_view(), name='register_customer'),
]