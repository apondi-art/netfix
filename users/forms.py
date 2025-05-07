from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, authenticate
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, Company, Customer


class DateInput(forms.DateInput):
    input_type = 'date'


def validate_email(value):
    # In case the email already exists in an email input in a registration form, this function is fired
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            value + " is already taken.")
    
class CustomerSignUpForm(UserCreationForm):
    birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Enter your date of birth'}),
        label="Date of Birth"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'password1', 'password2', 'birth')
        labels = {
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

    def __init__(self, *args, **kwargs):
        super(CustomerSignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
        self.fields['birth'].widget.attrs.update({'autocomplete': 'off'})

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
            Customer.objects.create(user=user, birth=self.cleaned_data['birth'])
        return user


class CompanySignUpForm(UserCreationForm):
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
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'field')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = [('', '--- Select Field ---')] + list(Company.FIELD_CHOICES)
        
        # Set common attributes for all fields
        field_attrs = {
            'class': 'form-control',
            'autocomplete': 'off'
        }
        
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
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    @transaction.atomic
    def save(self, commit=True):
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
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'off'
