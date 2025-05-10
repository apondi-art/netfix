from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Company, Customer


class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price_hour = models.DecimalField(decimal_places=2, max_digits=100)
    rating = models.IntegerField(validators=[MinValueValidator(
        0), MaxValueValidator(5)], default=0)
    choices = (
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
    field = models.CharField(max_length=30, blank=False,
                             null=False, choices=choices)
    date = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name



class ServiceRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='requests')
    hours = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    request_date = models.DateTimeField(auto_now_add=True)
    additional_notes = models.TextField(blank=True, null=True)
    status_choices = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='PENDING')

    def save(self, *args, **kwargs):
        # Calculate price based on service hourly rate and requested hours
        if not self.price:
            self.price = self.service.price_hour * self.hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.user.username} - {self.service.name} - {self.status}"
