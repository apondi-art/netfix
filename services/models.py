from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Company, Customer


class Service(models.Model):
    """
    Represents a service offered by a company.
    
    Attributes:
        company (ForeignKey): Company providing the service
        name (CharField): Name of the service (max 40 chars)
        description (TextField): Detailed service description
        price_hour (DecimalField): Hourly rate with 2 decimal places
        rating (IntegerField): Service rating (0-5 scale)
        field (CharField): Category of service from predefined choices
        date (DateTimeField): Last modification timestamp (auto-updated)
    """
    
    # Service category choices (constant)
    SERVICE_CATEGORIES = (
        ('Air Conditioner', 'Air Conditioner'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('House Keeping', 'House Keeping'),
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price_hour = models.DecimalField(decimal_places=2, max_digits=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    field = models.CharField(
        max_length=30,
        blank=False,
        null=False,
        choices=SERVICE_CATEGORIES
    )
    date = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        """String representation of the service."""
        return self.name


class ServiceRequest(models.Model):
    """
    Represents a customer's request for a specific service.
    
    Attributes:
        customer (ForeignKey): Customer making the request
        service (ForeignKey): Requested service
        hours (PositiveIntegerField): Duration in hours
        location (CharField): Service location address
        price (DecimalField): Total calculated price
        request_date (DateTimeField): Creation timestamp (auto-added)
        additional_notes (TextField): Optional customer notes
        status (CharField): Current status from predefined choices
    """
    
    # Request status choices (constant)
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    hours = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    request_date = models.DateTimeField(auto_now_add=True)
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    def save(self, *args, **kwargs):
        """
        Overrides save method to auto-calculate price if not set.
        Price = service hourly rate * requested hours.
        """
        if not self.price:
            self.price = self.service.price_hour * self.hours
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the service request."""
        return f"{self.customer.user.username} - {self.service.name} - {self.status}"