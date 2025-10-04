from django.contrib.auth.backends import ModelBackend
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from django.shortcuts import render
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
from .lib import CustomPermDoubleClass,get_id,is_authenticate,send_email
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from .s import *
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes,force_str
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
        return JsonResponse({"error": "Данных не хватает"}, status=400)
        
    if email is None and username is None:
        return JsonResponse({"error": "Данных не хватает"}, status=400)
    
    if email is None:
        return JsonResponse({"error": "Данных не хватает"}, status=400)
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email уже занят"}, status=403)
    

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username уже занят"}, status=403)
    


    user = User.objects.create_user(username=username,email=email,password=password,is_active=False)
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_link = f"{settings.HOST}/accounts/google/verify/{uidb64}/{token}/"
    
    send_email([email],"Перейдите по ссылке для потверждения аккаунта",verify_link)

    return JsonResponse({"data":verify_link},status=200)


    
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

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # Декодируем uidb64, чтобы получить ID пользователя
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return JsonResponse({"error": "Неверная ссылка"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, активен ли пользователь
        if user.is_active:
            return JsonResponse({"error": "Аккаунт уже подтверждён"}, status=status.HTTP_403_FORBIDDEN)

        # Проверяем токен
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return JsonResponse({"status": "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "Токен недействителен или просрочен"}, status=status.HTTP_400_BAD_REQUEST)
class BucketViewList(APIView):
    permission_classes = [CustomPermDoubleClass,]

    def get(self,request):
        user = get_object_or_404(Profile,pk=get_id(request))
        items = user.cart_items.all()
        serializer = OrderItem_S(items, many=True)
        return Response(serializer.data) 

    def post(self, request):
        user = get_object_or_404(Profile, pk=get_id(request))
        product_id = request.data.get('product')  # ожидаем, что приходит id продукта
        count = int(request.data.get('count', 1))  # количество по умолчанию = 1

        if not product_id:
            return Response({"error": "product is required"}, status=400)

        
        item, created = OrderItem.objects.get_or_create(
            user=user,
            product_id=product_id,
            defaults={'count': 1}
        )

        if not created:
            item.count += count
            item.save()

        serializer = OrderItem_S(item, context={'request': request})
        return Response(serializer.data, status=201)
    
class BucketViewDetail(APIView):
    permission_classes = [CustomPermDoubleClass,]

    def put(self, request, pk):
        user = get_object_or_404(Profile,pk=get_id(request))
        item = get_object_or_404(user.cart_items, pk=pk)
        operation = request.data.get("operation",None)
        if operation is None:
            return Response(status=status.HTTP_409_CONFLICT)
        
        serializer = OrderItem_S(item, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()

            if operation.isdigit():
                new_count = int(operation)
                if new_count > 0:
                    item.count = new_count
                    item.save()
                elif new_count == 0:
                    item.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)

            if operation == "inc":
                item.count += 1
                item.save()
            if operation == "dec":
                if item.count <= 1:
                    item.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    item.count -= 1
                    item.save()

            return Response(OrderItem_S(item).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(Profile,pk=get_id(request))
        item = get_object_or_404(user.cart_items, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
def reset_password(request):
    if request.method != "POST":
        return JsonResponse({"error":"Method not allowed"},status=503)
    
    email = request.POST.get("email",None)
    if not email:
        return JsonResponse({"error":"Не хватает данных"},status=400)
    
    user = User.objects.filter(email=email).first()
    if user is None:
        return JsonResponse({"error":"Нет такого пользователя"},status=403)
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_link = f"{settings.HOST}/accounts/password/verify/{uidb64}/{token}/"
    
    send_email([email],"Зайдите по ссылке для сброса пароля",verify_link)

    return JsonResponse({"data":"Ok"},status=200)




class VerifyResetPassword(APIView):
    template_name = "reset.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse("Неверная или устаревшая ссылка", status=400)

        if default_token_generator.check_token(user, token):
            return render(request, self.template_name, {
                "uidb64": uidb64,
                "token": token
            })
        else:
            return HttpResponse("Ссылка недействительна или уже использована", status=400)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({"error": "Неверная ссылка"}, status=400)

        if not default_token_generator.check_token(user, token):
            return JsonResponse({"error": "Ссылка недействительна"}, status=400)

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            return JsonResponse({"error": "Введите пароль дважды"}, status=400)
        if password1 != password2:
            return JsonResponse({"error": "Пароли не совпадают"}, status=400)

        user.set_password(password1)
        user.save()

        response = HttpResponseRedirect(settings.FRONTEND_URL)
        return response
    
@csrf_exempt
def getUser(request):
    user = is_authenticate(request)
    if not user:
        return HttpResponse("Forbidden",status=403)
    return JsonResponse(Profile_s(user).data,status=200)



def getInfo(request):
    obj = Info.objects.last()

    if obj is None:
        return JsonResponse({"data":"Not Info obj"},status=500)
    
    return JsonResponse(Info_s(obj,context={"request":request}).data,status=200)

