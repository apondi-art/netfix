from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports multiple user types (company/customer) with email as the primary identifier.
    """
    
    is_company = models.BooleanField(
        default=False,
        help_text="Designates whether this user is a company account"
    )
    is_customer = models.BooleanField(
        default=False,
        help_text="Designates whether this user is a customer account"
    )
    email = models.EmailField(
        unique=True,
        help_text="Required. Must be a valid and unique email address"
    )
    
    # Authentication configuration
    USERNAME_FIELD = 'email'  # Use email as the authentication identifier
    REQUIRED_FIELDS = ['username']  # Additional required fields for createsuperuser

    class Meta:
        """Meta options for the User model"""
        db_table = 'users_user'  # Custom database table name


class Customer(models.Model):
    """
    Customer profile model containing customer-specific information.
    Extends the base User model with a one-to-one relationship.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        help_text="Reference to the associated User account"
    )
    birth = models.DateField(
        help_text="Customer's date of birth"
    )

    def __str__(self):
        """String representation of the customer"""
        return f"Customer: {self.user.username}"


class Company(models.Model):
    """
    Company profile model containing company-specific information.
    Extends the base User model with a one-to-one relationship.
    Includes service field choices and rating system.
    """
    
    # Available service fields for companies
    FIELD_CHOICES = [
        ('Air Conditioner', 'Air Conditioner'),
        ('All in One', 'All in One'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('House Keeping', 'House Keeping'),
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='company',
        help_text="Reference to the associated User account"
    )
    field = models.CharField(
        max_length=70,
        choices=FIELD_CHOICES,
        blank=False,
        null=False,
        default='All in One',
        help_text="Primary service field of the company"
    )
    is_all_in_one = models.BooleanField(
        default=False,
        help_text="Designates whether the company provides all services"
    )
    rating = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(0)],
        default=0,
        help_text="Company rating from 0 to 5 stars"
    )

    class Meta:
        """Meta options for the Company model"""
        db_table = 'users_company'  # Custom database table name

    def __str__(self):
        """String representation of the company"""
        if self.is_all_in_one or self.field == 'All in One':
            return f"{self.user.username} (All Services)"
        return f"{self.user.username} ({self.field})"