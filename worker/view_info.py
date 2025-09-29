from custom_auth.models import *
from rest_framework.generics import RetrieveAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import mixins, viewsets
from catalog.pag import *
from catalog.s import *
from custom_auth.lib import CustomPermTriClass
from django.views.decorators.csrf import csrf_exempt
import json


class CategoryViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    permission_classes = [CustomPermTriClass,]
    queryset = Category.objects.all()
    serializer_class = Category_s



class BrandViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    permission_classes = [CustomPermTriClass,]
    queryset = Brand.objects.all()
    serializer_class = Brand_s




