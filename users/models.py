from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator



class User(AbstractUser):
    is_company = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users_user'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth = models.DateField()


class Company(models.Model):

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
          related_name= 'company'
          )
    field = models.CharField(
         max_length=70, 
         choices=  FIELD_CHOICES,
         blank= False,
         null = False,
         default='All in One'
    )
    is_all_in_one = models.BooleanField(default=False)
    rating = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(0)], 
        default=0
        )
    class Meta:
        db_table = 'users_company'

    def __str__(self):
          if self.is_all_in_one  or self.field == 'All in One':
            return f"{self.user.username} (All in One)"
          return f"{self.user.username} ({self.field})"


   