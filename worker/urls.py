from django.urls import path
from .views import *
from .view_product import *

urlpatterns = [
    path("refresh/products/",refresh_products),
    path("refresh/event/",refresh_events),
    path("getInfo/",info_get),

    path("events/",EventListView.as_view()),   
    path("events/<int:pk>",EventDetailView.as_view()),   


    path("products/",ProductsView.as_view()),
    path("products/<int:pk>",ProductDetail.as_view()),


    path("add/product/",addProduct),
    path("edit/product/<int:id>",editProduct)

]


