from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
import re
from rest_framework.pagination import PageNumberPagination
import math
from .models import *
from .s import *



def _bool_param(v):
    if v is None:
        return None
    v = str(v).lower()
    return v in ("1", "true", "yes", "y", "on")


class ProductPagination(PageNumberPagination):
    page_size = 4
    
    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        num_pages = math.ceil(total_count / page_size) if page_size else 1

        return Response({
            "count": total_count,
            "num_pages": num_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by("-id")
    serializer_class = GallerySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("-id")
    serializer_class = CategorySerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("-id")
    serializer_class = BrandSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-id")
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    detail_serializer = ProductDetail_s
    
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=["get"], url_path="filter")
    def filter(self, request):
        qs = Product.objects.all()

        # --- Category ---
        category = request.query_params.get("category")
        if category:
            ids = [int(x) for x in re.findall(r"\d+", category)]
            if ids:
                qs = qs.filter(category_id__in=ids)

        # --- Brand ---
        brand = request.query_params.get("brand")
        if brand:
            ids = [int(x) for x in brand.split(",") if x.strip().isdigit()]
            if ids:
                qs = qs.filter(brand_id__in=ids)

        # --- Price ---
        try:
            min_price = float(request.query_params.get("min_price", 0) or 0)
            qs = qs.filter(price__gte=min_price)
        except ValueError:
            pass

        try:
            max_price = float(request.query_params.get("max_price") or 0)
            if max_price > 0:
                qs = qs.filter(price__lte=max_price)
        except ValueError:
            pass

        # --- Stock ---
        in_stock = _bool_param(request.query_params.get("in_stock"))
        if in_stock is True:
            qs = qs.filter(count__gt=0)
        elif in_stock is False:
            qs = qs.filter(count__lte=0)

        # --- Sale ---
        on_sale = _bool_param(request.query_params.get("on_sale"))
        if on_sale is True:
            qs = qs.filter(discount__gt=0)
        elif on_sale is False:
            qs = qs.filter(discount__lte=0)

        # --- New products ---
        new_flag = _bool_param(request.query_params.get("new"))
        if new_flag:
            new_days = request.query_params.get("new_days", 7)
            try:
                n = int(new_days)
            except ValueError:
                n = 7
            since = timezone.now() - timedelta(days=n)
            qs = qs.filter(date__gte=since)

        # --- Tags search (AND logic, можно поменять на OR) ---
        tags = request.query_params.get("tags")
        if tags:
            tokens = [normalize_text_for_db(t).strip() for t in tags.split(",") if t.strip()]
            if tokens:
                q_obj = Q()
                for tk in tokens:
                    q_obj &= Q(normalized_text__icontains=tk)
                qs = qs.filter(q_obj)

        # --- Global search q ---
        q = request.query_params.get("q")
        if q:
            tokens = [t for t in normalize_text_for_db(q).split() if t]
            if tokens:
                q_obj = Q()
                for tk in tokens:
                    q_obj |= (Q(title__icontains=tk) | Q(desc__icontains=tk))
                qs = qs.filter(q_obj)
        

        # --- Ordering ---
        ordering = request.query_params.get("ordering", "-date")
        allowed = {"price", "-price", "date", "-date", "id", "-id"}
        if ordering not in allowed:
            ordering = "-date"
        qs = qs.order_by(ordering)

        # --- Paginate ---
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)