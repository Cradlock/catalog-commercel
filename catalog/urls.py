from django.urls import path
from .views import *


urlpatterns = [
    path("categories/",CategoryListView.as_view()),
    path("brands/",BrandsListView.as_view()),
    path("products/",ProductListView.as_view()),
    path("products/<int:id>",ProductDetailView.as_view()),


# filter: price,discount,category,brand


# search: title


# classification filter: по акции,по новизне,популярные


]
