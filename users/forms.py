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


class CompanySignUpForm(UserCreationForm):
  pass


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
