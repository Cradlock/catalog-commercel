from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from custom_auth.views import getInfo

urlpatterns = [
    path('info/', getInfo),
    path('admin/', admin.site.urls),
    path('api/',include("catalog.urls")),
    path('accounts/',include("custom_auth.urls")),
    path('admin_api/',include("worker.urls"))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
