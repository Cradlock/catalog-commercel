import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission 
from django.core.mail import send_mail
from django.conf import settings
from custom_auth.models import Profile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

User = get_user_model()
import re

def is_valid_phone(number):

    clean_number = re.sub(r"[ \-\(\)]", "", number)
    
    # Проверяем формат: может начинаться с +, далее только цифры
    if not re.fullmatch(r"\+?\d+", clean_number):
        return False
    
    # Проверяем длину номера (пример: 11-12 цифр для России)
    digits_only = re.sub(r"\D", "", clean_number)  # только цифры
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    return True

def send_email(recipient:str,msg:str,link:str):
    subject = "Тестовое письмо"
    message = f"{msg} -> {link}"
    from_email = settings.GOOGLE_OWNER
    password = settings.EMAIL_PASSWORD

    message = MIMEMultipart("alternative")
    message["From"] = from_email
    message["To"] = recipient
    message["Subject"] = f"Сообщения от DTS ({msg})"

    text = ""
    html = f"""
<html>
  <body>
    <p>Привет!<br>
       <a href="{link}">Нажми здесь для{msg}</a>
    </p>
  </body>
</html>
    """
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")





def is_authenticate(request) -> bool:
    token = request.COOKIES.get("access_token")
    if not token:
        return False
    
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")
        if not user_id:
            return False
        
        user = Profile.objects.get(id=user_id)
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
