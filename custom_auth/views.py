from django.contrib.auth.backends import ModelBackend
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
import datetime
import jwt
import requests
from .models import *
from .lib import CustomPermDoubleClass,get_id
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from .s import *
from django.shortcuts import get_object_or_404

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
        

        random_password = get_random_string(length=12) 
        user, created = User.objects.get_or_create(email=email, defaults={"username": username,"password": make_password(random_password)})
        
        # Создаём JWT токен
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        

        is_admin = user.is_staff or user.is_superuser



        # Редирект на фронтенд с cookie
        response = HttpResponseRedirect(settings.FRONTEND_URL+f"?is_admin={'true' if is_admin else 'false'}")
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True, 
            secure=True,  
            samesite="None",
            domain=urlparse(settings.HOST).hostname ,     # привязка к домену бэка
            path="/",
            max_age=24*60*60
        )

        return response
    

@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed",status=500) 
    
    username = request.POST.get("username")
    password = request.POST.get("password")

    if username is None:
        return  HttpResponse("Not enough data",status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return HttpResponse("Unauthorized",status=401)
        
    if user.check_password(password):
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        

        is_admin = user.is_staff or user.is_superuser

        res = JsonResponse({"is_admin": is_admin}, status=200)
        res.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True, 
            secure=True,  
            samesite="None",
            domain=urlparse(settings.HOST).hostname,  
            path="/",
            max_age=24*60*60
        )

        return res
    
    
    return HttpResponse("Unautorized",status=401)

@csrf_exempt
def signup_view(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed",status=500)
    
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    if password is None:
        return HttpResponse("Not enough data",status=400)
    
    if username is None:
        user = User.objects.create_user(email=email,password=password)

    if email is None:
        pass 

    if email is None and username is None:
        return HttpResponse("Not enough data",status=400)
    
@csrf_exempt
def logout_view(request):
    response = HttpResponseRedirect(settings.FRONTEND_URL)
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite="None",
        path="/",
        domain=urlparse(settings.HOST).hostname,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        max_age=0
    )
    return response



class BucketViewList(APIView):
    permission_classes = [CustomPermDoubleClass,]

    def get(self,request):
        user = get_object_or_404(Profile,pk=get_id(request))
        items = user.cart_items.all()
        serializer = OrderItem_S(items, many=True)
        return Response(serializer.data) 

    def post(self,request):
        user = get_object_or_404(Profile,pk=get_id(request))
        serializer = OrderItem_S(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 



class BucketViewDetail(APIView):
    permission_classes = [CustomPermDoubleClass,]

    def put(self, request, pk):
        user = get_object_or_404(Profile,pk=get_id(request))
        item = get_object_or_404(user.cart_items, pk=pk)
        serializer = OrderItem_S(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(Profile,pk=get_id(request))
        item = get_object_or_404(user.cart_items, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)








def getInfo(request):
    obj = Info.objects.last()

    if obj is None:
        return JsonResponse({"data":"Not Info obj"},status=500)
    
    return JsonResponse(Info_s(obj,context=request).data,status=200)

