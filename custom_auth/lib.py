import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission 
User = get_user_model()


def is_authenticate(request) -> bool:
    token = request.COOKIES.get("access_token")
    if not token:
        return False
    
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")
        if not user_id:
            return False
        
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return False
        return user

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return False

def is_admin(request) -> bool:
    token = request.COOKIES.get("access_token")
    if not token:
        return False
    
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")
        if not user_id:
            return False
        
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return False
        if user.is_staff:
            return user
        return False

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return False

def get_id(request) -> int:
    token = request.COOKIES.get("access_token")
    if not token:
        return -1
    
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")
        if not user_id:
            return -1
        

        
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return False
        return user_id

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return -1

class CustomPermClass(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request)

    def has_object_permission(self, request, view, obj):
        return is_admin(request)


class CustomPermDoubleClass(BasePermission):
    def has_permission(self, request, view):
        return is_authenticate(request)

    def has_object_permission(self, request, view, obj):
        return is_authenticate(request)



class CustomPermTriClass(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return is_admin(request)

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return is_admin(request)
