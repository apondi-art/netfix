from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, TemplateView
from django.db import transaction
from django.contrib import messages
from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm
from .models import User, Company, Customer

def register(request):
    """
    Registration landing page view.
    Renders the registration type selection template.
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Rendered registration selection page
    """
    return render(request, 'users/register.html')

class CustomerSignUpView(CreateView):
    """
    Class-based view for customer registration.
    Handles customer account creation using CustomerSignUpForm.
    Inherits from Django's CreateView for form processing.
    """
    model = User
    form_class = CustomerSignUpForm
    template_name = 'users/register_customer.html'

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to the template.
        
        Returns:
            dict: Context data with user_type set to 'customer'
        """
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """
        Processes valid form submission.
        Creates user account, logs in user, and redirects to home page.
        
        Args:
            form: Validated CustomerSignUpForm instance
            
        Returns:
            HttpResponseRedirect: Redirect to home page
        """
        user = form.save()
        login(self.request, user)
        return redirect('/')

class CompanySignUpView(CreateView):
    """
    Class-based view for company registration.
    Handles company account creation using CompanySignUpForm.
    Includes success/error messaging and transaction safety.
    """
    model = User
    form_class = CompanySignUpForm
    template_name = 'users/register_company.html'

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to the template.
        
        Returns:
            dict: Context data with user_type set to 'company'
        """
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        """
        Processes valid form submission with error handling.
        Creates user account, logs in user, sets success message,
        and redirects to home page. On failure, displays error message.
        
        Args:
            form: Validated CompanySignUpForm instance
            
        Returns:
            HttpResponse: Redirect on success or re-rendered form on failure
        """
        try:
            user = form.save()
            login(self.request, user)
            messages.success(
                self.request,
                f'Account created successfully for {user.email}'
            )
            return redirect('/')
            
        except Exception as e:
            messages.error(
                self.request,
                f'Registration failed: {str(e)}'
            )
            return self.form_invalid(form)

def LoginUserView(request):
    """
    Custom login view handling user authentication.
    Supports both GET (form display) and POST (form submission) methods.
    Uses UserLoginForm for email/password validation.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered login page or redirect on success
    """
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate user with email/password
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                # Add non-field error for invalid credentials
                form.add_error(None, 'Invalid email or password')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})