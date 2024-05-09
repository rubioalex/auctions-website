from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    
    gender_choices = models.TextChoices("Gender", "Male Female None")
    gender = models.CharField(choices=gender_choices, max_length=10)
    
    
def validate_min_price(value):
    if value < 1:
        raise ValidationError('Price must be greater than 0.')
    pass


class Category(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name.title()


class Listing(models.Model):    
    object_name = models.CharField(max_length=50)
    description = models.CharField(max_length=600, blank=True, null=True)
    image = models.ImageField(upload_to='listings_images', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='listings', on_delete=models.CASCADE)
    
    is_closed = models.BooleanField(default=False)
    
    starting_bid = models.FloatField(validators=[validate_min_price])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    
    def __str__(self):
        return self.object_name.title()
    
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['user', 'listing']
    
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    amount = models.FloatField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    
    def __str__(self):
        return f"Bid by {self.user.username} of {self.amount}"

    
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    comment_body = models.CharField(max_length=500, default=None)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"