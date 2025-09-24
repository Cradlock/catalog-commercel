from custom_auth.models import *
from rest_framework.generics import RetrieveAPIView,ListAPIView
from catalog.pag import *
from catalog.s import *
from custom_auth.lib import is_admin
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

class ProductsView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = Product_s
    pagination_class = CustomPagination


class ProductDetail(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetail_s


@csrf_exempt
def addProduct(request):
    if not is_admin(request):
        return HttpResponse("Foribbden",status=403)
    
    if request.method != "POST":
        return HttpResponse("Method not alowwed",status=405)

    title = request.POST.get("title")
    desc = json.loads(request.POST.get("desc"))
    discount = float(request.POST.get("discount"))
    count = request.POST.get("count")
    category_id = int(request.POST.get("category"))
    brand_id = int(request.POST.get("brand"))
    price = int(request.POST.get("price"))

    cover = request.FILES.get("cover")
    images_gallery = request.FILES.getlist("gallery")
    
    category = Category.objects.filter(id=category_id).first()
    brand = Brand.objects.filter(id=brand_id).first()

    product = Product.objects.create(
        title=title,
        desc=desc,
        price=price,
        discount=discount,
        count=count,
        category=category,
        brand=brand,
        cover=cover, 
    )

    for i in images_gallery:
        Gallery.objects.create(file=i,product=product)

    return HttpResponse("ok",status=200)
    

@csrf_exempt
def editProduct(request, id):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    product = Product.objects.filter(id=id).first()
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    title = request.POST.get("title")
    if title is not None:
        product.title = title

    desc = request.POST.get("desc")
    if desc is not None:
        try:
            product.desc = json.loads(desc)  
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in 'desc'"}, status=400)

    discount = request.POST.get("discount")
    if discount is not None:
        try:
            product.discount = float(discount)
        except ValueError:
            return JsonResponse({"error": "Invalid discount"}, status=400)

    count = request.POST.get("count")
    if count is not None:
        try:
            product.count = int(count)
        except ValueError:
            return JsonResponse({"error": "Invalid count"}, status=400)

    price = request.POST.get("price")
    if price is not None:
        try:
            product.price = int(price)
        except ValueError:
            return JsonResponse({"error": "Invalid price"}, status=400)

    category_id = request.POST.get("category")
    if category_id is not None:
        category = Category.objects.filter(id=int(category_id)).first()
        product.category = category

    brand_id = request.POST.get("brand")
    if brand_id is not None:
        brand = Brand.objects.filter(id=int(brand_id)).first()
        product.brand = brand

    cover = request.FILES.get("cover")
    if cover:
      if product.cover:
        product.cover.delete(save=False)
    product.cover = cover   

    deleted_gallery = request.POST.getlist("deleted_gallery")

    if len(deleted_gallery) != 0:
        for idx in deleted_gallery:
            try:
                img = Gallery.objects.get(pk=int(idx))
                img.file.delete(save=False)
                img.delete()
            except Gallery.DoesNotExist:
                pass
    
    images_count = len(request.FILES)

    if images_count != 0:
        for key,value in request.FILES.items():
            if key == "-1":
                Gallery.objects.create(product=product,file=value) 
            elif int(key) > 0:
                gallery = Gallery.objects.get(pk=int(key))
                gallery.file = value
                gallery.save()
            
    product.save()
    return JsonResponse({"data": Product_s(product).data}, status=200)


@csrf_exempt
def edit_product_mass(request):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    

    indices = request.POST.getlist("indices")
    
    if indices is None or len(indices) == 0:
        return HttpResponse("Ok",status=200)
    
    title = request.POST.get("title")
    price = request.POST.get("price")
    discount = request.POST.get("discount")
    count = request.POST.get("count")
    category = request.POST.get("category")
    brand = request.POST.get("brand")
    cover = request.POST.get("cover")


    oper,desc = request.POST.get("desc")
    
    images = request.FILES





@csrf_exempt
def deleteProduct(request, id):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    product = Product.objects.filter(id=id).first()
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    galleries = Gallery.objects.filter(product=product)
    for g in galleries:
        if g.file:  
            g.file.delete(save=False)
    galleries.delete()

    if product.cover:
        product.cover.delete(save=False)

    product.delete()

    return JsonResponse({"message": "Product deleted successfully"}, status=200)



@csrf_exempt
def getProduct(request):
    if not is_admin(request):
        return HttpResponse("Forbidden", status=403)
    
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)
    
    try:
        page = int(request.GET.get("page", 1))  # текущая страница (1-based)
        page_size = int(request.GET.get("size", 10))  # элементов на страницу
        if page < 1: page = 1
        if page_size < 1: page_size = 10
    except ValueError:
        page = 1
        page_size = 10

    # Все объекты Product
    products_qs = Product.objects.all().order_by("id")
    total_count = products_qs.count()
    
    # Рассчёт границ среза
    start = (page - 1) * page_size
    end = start + page_size

    # Сериализация объектов
    products_page = products_qs[start:end]
    serialized_products = Product_s(products_page, many=True).data

    # Определяем ссылки на страницы
    base_url = request.build_absolute_uri(request.path)
    next_page = page + 1 if end < total_count else None
    previous_page = page - 1 if start > 0 else None

    # Формируем URL для следующей/предыдущей страницы
    def build_page_url(p):
        return f"{base_url}?page={p}&size={page_size}"

    response = {
        "count": total_count,
        "next": build_page_url(next_page) if next_page else None,
        "previous": build_page_url(previous_page) if previous_page else None,
        "results": serialized_products
    }

    return JsonResponse(response, safe=False)


