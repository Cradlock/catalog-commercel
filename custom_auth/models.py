from django.db import models
from catalog.models import *
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid



class Profile(AbstractUser):
    email = models.EmailField(unique=True)
    is_cashier = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=30,default="",blank=True,null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class OrderItem(models.Model):
    count = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='cart_items')
    
    class Meta:
        unique_together = ('user', 'product')
class Info(models.Model):
    cashier_numbers = models.JSONField()
    title = models.CharField(max_length=255)
    logo = models.FileField()
    contact_number = models.CharField(max_length=35,default="")
    telegramm = models.CharField(max_length=200,blank=True)
    instagramm = models.CharField(max_length=200,blank=True)
    whatsapp = models.CharField(max_length=200,blank=True)
    gmail = models.EmailField(blank=True,null=True,default=None)
    


    
class Event(models.Model):
    is_special = models.BooleanField(default=False)
    type_special = models.CharField(null=True,blank=True,max_length=25)

    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True,null=True)
    
    title = models.CharField(max_length=255)
    desc = models.TextField()

    discount_precent = models.FloatField(default=1.0)

    brands = models.ManyToManyField(Brand)
    categories = models.ManyToManyField(Category)


    def __str__(self):
        return self.title

class GalleryEvent(models.Model):
    file = models.ImageField()
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE,related_name="gallery")



class Order(models.Model):
    created_date = models.DateTimeField()
    products = models.JSONField(default=list)
    total_price = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='orders')
    client_number = models.CharField(max_length=30, null=True, blank=True)


class Cheque(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    products = models.JSONField(default=list)
    price = models.PositiveIntegerField()
    client = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True)
    client_number = models.CharField(max_length=30)




