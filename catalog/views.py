from .models import *
from .s import *
from .pag import *
from rest_framework import generics







class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = Category_s
    

class BrandsListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = Brand_s


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = Product_s
    pagination_class = CustomPagination


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = Product_s

    