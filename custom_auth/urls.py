from django.urls import path,include
from .views import *


urlpatterns = [
    # login reset-password
    path("", include("dj_rest_auth.urls")),  
    # signup
    path("signup/", include("dj_rest_auth.registration.urls")),
    # logout
    path("logout/", include("dj_rest_auth.urls")),  
    # google login
    path("google/login/", GoogleRedirectView.as_view()),
    path("google/callback/", GoogleCallbackView.as_view()),

]



# get-busket/
# add-busket/ 
# del-busket/
