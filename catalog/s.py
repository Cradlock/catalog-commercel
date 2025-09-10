from rest_framework import serializers as S
from .models import * 



class Category_s(S.ModelSerializer):
    class Meta:
        model = Category
        fields = ["pk","title"]


class Brand_s(S.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["pk","title"]


class Product_s(S.ModelSerializer):

    class Meta:
        model = Product 
        fields = "__all__"


class Gallery_s(S.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ["pk","file"]

