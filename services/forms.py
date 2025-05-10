from django import forms
from .models import Service
from users.models import Company


class CreateNewService(forms.Form):
    """
    Form for creating a new service offering.
    
    Fields:
        name (CharField): Name of the service (max 40 chars)
        description (CharField): Detailed description of the service (textarea)
        price_hour (DecimalField): Hourly rate (2 decimal places, max 5 digits)
        field (ChoiceField): Category/field of service (dropdown selection)
    """
    
    name = forms.CharField(max_length=40)
    description = forms.CharField(widget=forms.Textarea, label='Description')
    price_hour = forms.DecimalField(
        decimal_places=2, max_digits=5, min_value=0.00)
    field = forms.ChoiceField(required=True)

    def __init__(self, *args, choices='', **kwargs):
        """
        Initialize form with dynamic choices and field attributes.
        
        Args:
            choices (tuple): Optional predefined choices for field dropdown
        """
        super(CreateNewService, self).__init__(*args, **kwargs)
        
        # Set choices for field dropdown - uses provided choices or defaults to Service.choices
        self.fields['field'].choices = choices if choices else Service.choices
        
        # Configure field attributes
        self.fields['name'].widget.attrs['placeholder'] = 'Enter Service Name'
        self.fields['description'].widget.attrs['placeholder'] = 'Enter Description'
        self.fields['price_hour'].widget.attrs['placeholder'] = 'Enter Price per Hour'
        self.fields['name'].widget.attrs['autocomplete'] = 'off'  # Disable autocomplete for name field


class RequestServiceForm(forms.Form):
    """
    Form for requesting a service from a provider.
    
    Fields:
        location (CharField): Service location/address
        hours (IntegerField): Duration in hours (1-24)
        additional_notes (CharField): Optional special instructions
    """
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your address'})
    )
    hours = forms.IntegerField(
        min_value=1,
        max_value=24,
        initial=1,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Number of hours'})
    )
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Any additional information?'})
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Bootstrap-compatible class attributes."""
        super(RequestServiceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'  # Add Bootstrap form-control class