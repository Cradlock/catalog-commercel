import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

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
        return True

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
        if user.is_staff:
            return True
        return False

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return False