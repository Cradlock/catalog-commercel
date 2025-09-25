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
from custom_auth.lib import is_authenticate,is_admin,CustomPermClass
from custom_auth.models import Info
from custom_auth.s import Info_s
from rest_framework.response import Response


class LastObjectRetrieveAPIView(generics.GenericAPIView):
    
    queryset = Info.objects.all()
    serializer_class = Info_s
    permission_classes = [CustomPermClass,]

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().order_by('-id').first()  # Последний объект по id
        if not obj:
            return Response({"detail": "Not found"}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)



class info_get(LastObjectRetrieveAPIView):
    queryset = Info.objects.all()
    serializer_class = Info_s
    permission_classes = [CustomPermClass,]


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


