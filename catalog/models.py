from django.db import models
from datetime import timedelta



class Category(models.Model):
    title = models.CharField(max_length=100)
    range_update = models.DurationField(default=timedelta(hours=24))
    last_update = models.DateTimeField(auto_now_add=True)


class Brand(models.Model):
    title = models.CharField(max_length=100)
    range_update = models.DurationField(default=timedelta(hours=24))
    last_update = models.DateTimeField(auto_now_add=True)



class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=0)
    discount = models.FloatField(default=0)
    desc = models.TextField(default="")
    count = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)


    def __str__(self):
        return self.title
    


class Gallery(models.Model):
    file = models.ImageField()
    is_main = models.BooleanField(default=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)



