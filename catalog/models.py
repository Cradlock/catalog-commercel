from django.db import models
from datetime import timedelta
import os

def normalize_text_for_db(text : str) -> str:
    return text

class Category(models.Model):
    title = models.CharField(max_length=100)
    range_update = models.DurationField(default=timedelta(hours=24))
    last_update = models.DateTimeField(auto_now_add=True)
    discount = models.FloatField(default=1.0)


class Brand(models.Model):
    title = models.CharField(max_length=100)

class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=0)
    discount = models.FloatField(default=0)
    desc = models.JSONField(blank=True,null=True)
    count = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
    last_buy = models.DateTimeField(auto_now_add=True)
    cover = models.ImageField()

    def __str__(self):
        return self.title
    


class Gallery(models.Model):
    file = models.ImageField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="gallery_product")

    def save(self, *args, **kwargs):
        try:
            old_file = Gallery.objects.get(pk=self.pk).file
        except Gallery.DoesNotExist:
            old_file = None

        super().save(*args, **kwargs)

        if old_file and old_file != self.file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)



