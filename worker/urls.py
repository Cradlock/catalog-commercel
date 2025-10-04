from django.urls import path
from .views import *
from .view_product import *
from .view_info import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"category", CategoryViewSet,basename="category")
router.register(r"brands", BrandViewSet,basename="brands")

urlpatterns = [
    path("refresh/products/",refresh_products),
    path("refresh/event/",refresh_events),
    path("getInfo/",info_get.as_view()),
    path("setInfo/",info_edit),

    path("events/",EventListView.as_view()),   
    path("events/<int:pk>",EventDetailView.as_view()),   
    
    path("add/event/",addEvent),
    path("edit/event/<int:id>/",editEvent),
    path("delete/event/<int:id>/",deleteEvent),

    path("products/",ProductsView.as_view()),
    path("products/<int:pk>",ProductDetail.as_view()),


    path("add/product/",addProduct),
    path("edit/product/<int:id>",editProduct),
    path("delete/product/",deleteProduct),
    path("filter/products/",FiilterProduct.as_view()),

    path("check/cheque/<uuid:uuid>",check_cheque),
    path("create/order/",create_order),
    path("set/order/",set_order),
    path("orders/",OrdersViewList.as_view())

]

urlpatterns += router.urls


