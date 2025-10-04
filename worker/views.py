from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from custom_auth.models import *
from django.db.models import F,Q
from django.utils.timezone import now
from rest_framework import generics
from rest_framework import mixins,viewsets
from custom_auth.s import *
from custom_auth.models import *
from custom_auth.lib import is_authenticate,is_admin,CustomPermClass,get_id
from custom_auth.models import Info
from custom_auth.s import Info_s
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json


class LastObjectRetrieveAPIView(generics.GenericAPIView):
    
    queryset = Info.objects.all()
    serializer_class = Info_s
    permission_classes = [CustomPermClass,]

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().last() 
        if not obj:
            return Response({"detail": "Not found"}, status=200)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class info_get(LastObjectRetrieveAPIView):
    queryset = Info.objects.all()
    serializer_class = Info_s
    permission_classes = [CustomPermClass,]

@csrf_exempt
def info_edit(request):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    info, created = Info.objects.get_or_create(id=1,defaults={               
        "title": "Default Title",
        "logo": None,
        "telegramm": "",
        "instagramm": "",
        "whatsapp": "",
        "gmail": "",
        "contact_number": "",
        "cashier_numbers": request.POST.getlist("cashier_numbers",[]),
    })

    title = request.POST.get("title")
    telegramm = request.POST.get("telegramm")
    instagramm = request.POST.get("instagramm")
    whatsapp = request.POST.get("whatsapp")
    gmail = request.POST.get("gmail")
    contact_number = request.POST.get("contact_number")
    logo = request.FILES.get("logo")

    if title is not None:
        info.title = title
    if telegramm is not None:
        info.telegramm = telegramm
    if instagramm is not None:
        info.instagramm = instagramm
    if whatsapp is not None:
        info.whatsapp = whatsapp
    if gmail is not None:
        info.gmail = gmail
    if contact_number is not None:
        info.contact_number = contact_number
    if logo:
        if info.logo:
            info.logo.delete(save=False)
        info.logo = logo

    cashier_numbers = request.POST.getlist("cashier_numbers") 
    if cashier_numbers:
       info.cashier_numbers = cashier_numbers

    info.save()



    return JsonResponse({"data": Info_s(info,context={'request': request}).data}, status=200)



def refresh_products(request):
    if request.method != "GET":
        return JsonResponse({"error":"Method not allowed"},status=405)
        
    now_time = now()
    updated_products = 0

    categories = Category.objects.filter(last_update__lt = now_time - F("range_update"))
    
    for cat in categories:
        outdated_products = Product.objects.filter(
            category=cat,
            last_buy__lt=now_time - cat.range_update
        )

        count = outdated_products.update(
            discount=cat.discount
        )

        updated_products += count 

        cat.last_update = now_time
        cat.save(update_fields=["last_update"])

    return JsonResponse({"updated_products":updated_products},status=200)

def refresh_events(request):
    if request.method != "GET":
        return JsonResponse({"error":"Method not allowed"},status=405)
    

    events_active = Event.objects.filter(date_start__lt = F("date_end"))

    events_deactive = Event.objects.filter(date_start__gte = F("date_end"))
    
    active_events = list(events_active.values())
    deactive_events = list(events_deactive.values())

    events_deactive.delete()

    for event in events_active:
        q = Q()
        if event.categories.exists():
            q |= Q(category__in=event.categories.all())
        if event.brands.exists():
            q |= Q(brand__in=event.brands.all())
        if not q:
            continue

        products = Product.objects.filter(q)
        products.update(discount=event.discount_precent)

    return JsonResponse({"active":active_events,"deactivate":deactive_events},status=200)
    

    






# Events

class EventListView(generics.ListAPIView):
    serializer_class = Event_s
    queryset = Event.objects.all()

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Event_s
    queryset = Event.objects.all()

@csrf_exempt
def addEvent(request):
    # --- Проверка прав доступа ---
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)

    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    try:
        # --- Основные данные ---
        title = request.POST.get("title", "").strip()
        desc = request.POST.get("desc", "").strip()
        discount_precent = float(request.POST.get("discount_precent", 1.0))
        is_special = request.POST.get("is_special") == "true"
        type_special = request.POST.get("type_special", "").strip() or None

        # --- Проверяем даты ---
        date_start = parse_datetime(request.POST.get("date_start") or "")
        date_end = parse_datetime(request.POST.get("date_end") or "")

        if not title:
            return JsonResponse({"error": "Поле title обязательно"}, status=400)
        if not date_start:
            return JsonResponse({"error": "Поле date_start обязательно и должно быть валидной датой"}, status=400)

        # --- ManyToMany ---
        brand_ids = request.POST.getlist("brands")
        category_ids = request.POST.getlist("categories")

        brands = Brand.objects.filter(id__in=brand_ids)
        categories = Category.objects.filter(id__in=category_ids)

        # --- Создание события ---
        event = Event.objects.create(
            title=title,
            desc=desc,
            discount_precent=discount_precent,
            is_special=is_special,
            type_special=type_special,
            date_start=date_start,
            date_end=date_end,
        )

        # --- Связи ManyToMany ---
        if brands.exists():
            event.brands.set(brands)
        if categories.exists():
            event.categories.set(categories)

        # --- Галерея ---
        images_gallery = request.FILES.getlist("gallery")
        for img in images_gallery:
            GalleryEvent.objects.create(file=img, event_id=event)

        return JsonResponse(Event_s(event, context={'request': request}).data, status=201)

    except ValueError as e:
        return JsonResponse({"error": f"Ошибка данных: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)

@csrf_exempt
def editEvent(request, id):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    event = Event.objects.filter(id=id).first()
    if not event:
        return JsonResponse({"error": "Event not found"}, status=404)

    # Обновляем поля
    title = request.POST.get("title")
    if title is not None:
        event.title = title

    desc = request.POST.get("desc")
    if desc is not None:
        event.desc = desc

    discount_precent = request.POST.get("discount_precent")
    if discount_precent is not None:
        try:
            event.discount_precent = float(discount_precent)
        except ValueError:
            return JsonResponse({"error": "Invalid discount_precent"}, status=400)

    is_special = request.POST.get("is_special")
    if is_special is not None:
        event.is_special = is_special.lower() == "true"

    type_special = request.POST.get("type_special")
    if type_special is not None:
        event.type_special = type_special

    date_start = request.POST.get("date_start")
    if date_start:
        event.date_start = date_start
    else:
        event.date_start = None
    
    date_end = request.POST.get("date_end")
    if date_end:
        event.date_end = date_end
    else:
        event.date_end = None

    # Обновление ManyToMany
    brand_ids = request.POST.getlist("brands")
    brands = Brand.objects.filter(id__in=brand_ids)
    event.brands.set(brands)

    category_ids = request.POST.getlist("categories")
    categories = Category.objects.filter(id__in=category_ids)
    event.categories.set(categories)

    # Работа с галереей
    deleted_gallery = request.POST.getlist("deleted_gallery")
    for idx in deleted_gallery:
        try:
            img = GalleryEvent.objects.get(pk=int(idx))
            img.file.delete(save=False)
            img.delete()
        except GalleryEvent.DoesNotExist:
            pass

    new_images = request.FILES.getlist("gallery")
    for img in new_images:
        GalleryEvent.objects.create(file=img, event_id=event)

    event.save()
    return JsonResponse({"data": Event_s(event, context={'request': request}).data}, status=200)


@csrf_exempt
def deleteEvent(request, id):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    product = Event.objects.filter(id=id).first()
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    galleries = GalleryEvent.objects.filter(event_id=product)
    for g in galleries:
        if g.file:  
            g.file.delete(save=False)
    galleries.delete()


    product.delete()

    return JsonResponse({"message": "Product deleted successfully"}, status=200)






# cashier
@csrf_exempt
def check_cheque(request,uuid):
    obj = Cheque.objects.filter(id=uuid).first()
    if not obj:
        return HttpResponse("Not check",status=400)
    
    return JsonResponse(Cheque_s(obj).data,status=200)
    




@csrf_exempt
def create_order(request):
    user = is_authenticate(request)
    if not user:
        return HttpResponse("Forbidden",status=403)
    
    if request.method != "POST":
        return HttpResponse("Method not alowed",status=405)
    
    order_items = OrderItem.objects.filter(user=user)
    if not order_items.exists():
        return HttpResponse("No items in bucket", status=400)  
    
    product_list = []
    summa = 0
    for item in order_items:
        product_info = {
            "id":item.product.id,
            "title":item.product.title,
            "price":item.count * item.product.price,
            "count": item.count 
        }
        product_list.append(product_info)
        summa += product_info["price"]

    obj = Order.objects.create(user=user,created_date=timezone.now(),products=product_list,total_price=summa)
    order_items.delete()

    cashier_number = Info.objects.first().cashier_numbers

    return JsonResponse(Order_s(obj).data,status=200)



@csrf_exempt
def set_order(request):
    if not is_admin(request):
        return HttpResponse("Foribbden",status=403)

    if request.method != "POST":
        return HttpResponse("Method not alowed",status=400) 


    id_order = request.POST.get("order")
    if id_order is None:
        return HttpResponse("Data not enough",status=400)
    
    order = Order.objects.filter(pk=id_order).first()
    if not order:
        return HttpResponse("Not order",status=400)
    

    obj = Cheque(created_date=timezone.now(),products=order.products,price=order.total_price,client=order.user)


    order.delete()

    return JsonResponse(Cheque_s(obj).data,status=200)




