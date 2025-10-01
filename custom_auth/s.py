from rest_framework import serializers as S 
from .models import *

class Info_s(S.ModelSerializer):
    class Meta:
        model = Info 
        fields = "__all__"


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
    product_name = S.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'count']


class Order_s(S.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"