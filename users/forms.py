from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, authenticate
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from .models import User, Company, Customer


class DateInput(forms.DateInput):
    """Custom DateInput widget that uses HTML5 date input type"""
    input_type = 'date'


def validate_email(value):
    """
    Validates that the email is not already in use.
    
    Args:
        value (str): The email address to validate
        
    Raises:
        ValidationError: If the email is already registered
    """
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            value + " is already taken.")


class CustomerSignUpForm(UserCreationForm):
    """
    Form for customer registration, extending Django's UserCreationForm.
    Includes additional fields for customer-specific information.
    """
    
    birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'placeholder': 'Enter your date of birth'
        }),
        label="Date of Birth",
        help_text="Enter your date of birth"
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        }),
        label="Username",
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )

    class Meta(UserCreationForm.Meta):
        """Meta options for the form, specifying model and fields"""
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'birth')
        labels = {
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form and update widget attributes"""
        super().__init__(*args, **kwargs)
        # Update placeholder attributes for better UX
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
        self.fields['birth'].widget.attrs.update({'autocomplete': 'off'})

    def clean_birth(self):
        """
        Validate that the birth date is in the past and user is at least 18 years old.
        
        Returns:
            date: The validated birth date
            
        Raises:
            ValidationError: If birth date is invalid or user is under 18
        """
        birth = self.cleaned_data.get('birth')
        today = date.today()

        if birth > today:
            raise ValidationError("Birth date cannot be in the future.")
        if (today.year - birth.year) < 18 or (today.year - birth.year == 18 and 
            (today.month, today.day) < (birth.month, birth.day)):
            raise ValidationError("You must be at least 18 years old to sign up.")
        return birth

    @transaction.atomic
    def save(self, commit=True):
        """
        Save the user and create associated customer profile in a transaction.
        
        Args:
            commit (bool): Whether to save to database immediately
            
        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)
        user.is_customer = True
        
        if commit:
            user.save()
            Customer.objects.create(
                user=user, 
                birth=self.cleaned_data['birth']
            )
        return user


class CompanySignUpForm(UserCreationForm):
    """
    Form for company registration, extending Django's UserCreationForm.
    Includes additional fields for company-specific information.
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'business@example.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }),
        help_text="Required. Enter a valid business email address.",
        error_messages={
            'required': 'You must provide an email address',
            'invalid': 'Please enter a valid email address'
        }
    )
    
    field = forms.ChoiceField(
        choices=Company.FIELD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Select your primary service field",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        """Meta options for the form, specifying model and fields"""
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'field')

    def __init__(self, *args, **kwargs):
        """Initialize the form and set up field attributes"""
        super().__init__(*args, **kwargs)
        # Add empty choice for better UX
        self.fields['field'].choices = [('', '--- Select Field ---')] + list(Company.FIELD_CHOICES)
        
        # Set common attributes for all fields
        field_attrs = {
            'class': 'form-control',
            'autocomplete': 'off'
        }
        
        # Update attributes for each field
        for field_name, field in self.fields.items():
            field.widget.attrs.update(field_attrs)
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
                field.help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        """
        Validate that the email is not already in use and normalize it.
        
        Returns:
            str: The normalized and validated email
            
        Raises:
            ValidationError: If email is already registered
        """
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        """
        Save the user and create associated company profile in a transaction.
        
        Args:
            commit (bool): Whether to save to database immediately
            
        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)
        # Ensure all required fields are set
        user.email = self.cleaned_data['email']
        user.is_company = True
        user.username = self.cleaned_data['username'] 
        
        if commit:
            user.save()  # This saves username, email, and hashed password
            
            # Create company profile
            field_value = self.cleaned_data['field']
            company = Company(
                user=user,
                field=field_value,
                is_all_in_one=(field_value == 'All in One')
            )
            company.save()

            return user

    
class UserLoginForm(forms.Form):
    """
    Custom login form that uses email instead of username for authentication.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the form"""
        super(UserLoginForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'})
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form and set up field attributes"""
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'off'