from django.contrib.auth.backends import ModelBackend
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
import datetime
import jwt
import requests
from .models import *
User = Profile




class UsernameOrEmailBackend(ModelBackend):
    """
    Аутентификация пользователя по username или email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("email")
        try:
            # сначала ищем по username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # если не нашли — ищем по email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        # проверяем пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None






class GoogleRedirectView(APIView):
    

    def get(self,request):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_PUBLIC_ID,
            "redirect_uri": settings.HOST + "/accounts/google/callback/",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "consent"
        }
        from urllib.parse import urlencode
        url = f"{base_url}?{urlencode(params)}"
        return Response({"redirect_url": url})



class GoogleCallbackView(APIView):
    
    def get(self,request):
        code = request.GET.get("code")
        if not code:
            frontend_url = f"{settings.FRONTEND_URL}?login=error&reason=not_code_provided"
            response = HttpResponseRedirect(frontend_url)
            return response
        
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "code":code,
            "client_id": settings.GOOGLE_PUBLIC_ID,
            "client_secret": settings.GOOGLE_SECRET_KEY,
            "redirect_uri": settings.HOST + "/accounts/google/callback/",
            "grant_type": "authorization_code"
        }

        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            frontend_url = f"{settings.FRONTEND_URL}?login=error&reason=failed_to_get_token"
            response = HttpResponseRedirect(frontend_url)
            return response
        
        token_data = r.json()
        access_token = token_data.get("access_token")

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        r = requests.get(user_info_url, headers=headers)
        if r.status_code != 200:
            frontend_url = f"{settings.FRONTEND_URL}?login=error&reason=not_user_data"
            response = HttpResponseRedirect(frontend_url)
            return response
        
        user_data = r.json()
        email = user_data.get("email")
        username = email.split("@")[0]

        user, created = User.objects.get_or_create(email=email, defaults={"username": username})
        
        # Создаём JWT токен
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Редирект на фронтенд с cookie
        response = HttpResponseRedirect(settings.FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=False,  
            samesite="Lax",
            max_age=24*60*60
        )

        return response
    


