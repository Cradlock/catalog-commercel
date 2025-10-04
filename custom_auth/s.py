from rest_framework import serializers as S 
from .models import *
import random

class Info_s(S.ModelSerializer):
    random_cashier_number = S.SerializerMethodField()

    class Meta:
        model = Info 
        fields = "__all__"

    
    def get_random_cashier_number(self,obj):
        if obj.cashier_numbers:
            return random.choice(obj.cashier_numbers)
        return None


class EventGallery_s(S.ModelSerializer):
    file = S.ImageField(use_url=True)
    class Meta:
        model = GalleryEvent
        fields = ["file","pk"]

        
class Event_s(S.ModelSerializer):
    gallery = EventGallery_s(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class Cheque_s(S.ModelSerializer):

    class Meta:
        model = Cheque
        fields = "__all__"


class OrderItem_S(S.ModelSerializer):
    product_name = S.CharField(source='product.title', read_only=True)
    price = S.IntegerField(source='product.price', read_only=True)
    image = S.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'image', 'price', 'product_name', 'count']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.product.cover:
            if request:
                return request.build_absolute_uri(obj.product.cover.url)
            # fallback если request нет
            from django.conf import settings
            return f"{settings.HOST}{obj.product.cover.url}"
        return None

class Order_s(S.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"


class Profile_s(S.ModelSerializer): 
    bucket = OrderItem_S(   source='cart_items',many=True,read_only=True)
    class Meta:
        model = Profile
        fields = [ "username","bucket" ]