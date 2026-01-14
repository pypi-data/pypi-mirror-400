from rest import decorators as rd
from rest import views as rv
from pushit.models import Product, Release


@rd.url('product')
@rd.url('product/<str:pk>')
def rest_on_product(request, pk=None):
    if pk is not None:
        if isinstance(pk, str) and not pk.isdigit():
            obj = Product.objects.filter(oid=pk).last()
            if obj is not None:
                if request.method == "GET":
                    return obj.on_rest_get(request)
                elif request.method == "POST":
                    return obj.on_rest_post(request)
    return Product.on_rest_request(request, pk)


@rd.url('release')
@rd.url('release/<int:pk>')
def rest_on_release(request, pk=None):
    return Release.on_rest_request(request, pk)
