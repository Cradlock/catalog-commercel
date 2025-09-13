from django.db import models
from catalog.models import *
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    email = models.EmailField(unique=True)
    bucket = models.ManyToManyField(Product)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Info(models.Model):
    cashier_numbers = models.JSONField()
    mbank_numbers = models.JSONField()
    title = models.CharField(max_length=255)
    logo = models.FileField()

class Event(models.Model):
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(blank=True,null=True)
    
    title = models.CharField(max_length=255)
    desc = models.TextField()
    discount_precent_cat = models.FloatField(default=1)
    discount_precent_brand = models.FloatField(default=1)
    
    brands = models.ManyToManyField(Brand)
    categories = models.ManyToManyField(Category)


    def __str__(self):
        return self.title


class GalleryEvent(models.Model):
    file = models.ImageField()
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE)


class Cheque(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    product_id = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    price = models.PositiveIntegerField()
    client_id = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True)

