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

class ProductDetail_s(S.ModelSerializer):
    gallery = Gallery_s(source="gallery_product",many=True,read_only=True)

    class Meta:
        model = Product
        fields = [ "id",
            "title",
            "price",
            "discount",
            "desc",
            "count",
            "date",
            "cover",
            "category",
            "brand",
            "gallery", ]
        
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "title")


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ( "file","pk")

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "discount",
            "count",
            "date",
            "cover",
            "category",
            "brand",
        )
        read_only_fields = ("date",)


