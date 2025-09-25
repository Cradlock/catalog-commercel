from custom_auth.models import *
from rest_framework.generics import RetrieveAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import mixins, viewsets
from catalog.pag import *
from catalog.s import *
from custom_auth.lib import is_admin
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import BasePermission
import json


class CustomPermClass(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request)

    def has_object_permission(self, request, view, obj):
        return is_admin(request)


class CategoryViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = Category_s
    permission_classes = [CustomPermClass,]



class BrandViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    queryset = Brand.objects.all()
    serializer_class = Brand_s
    permission_classes = [CustomPermClass,]