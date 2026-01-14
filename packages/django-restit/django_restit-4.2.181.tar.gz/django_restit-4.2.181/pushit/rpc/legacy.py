from pushit.models import Product, Release
from rest import decorators as rd


@rd.urlPOST (r'^product$')
@rd.urlPOST (r'^product/(?P<product_id>\d+)$')
@rd.urlPOST (r'^product/uuid/(?P<uuid>\w+)$')
@rd.login_optional
def updateProduct(request, product_id=None, uuid=None):
    if not request.member:
        return restPermissionDenied(request)
    product = None
    if not product_id and not uuid:
        product = Product.createFromRequest(request, owner=request.member, group=request.group)
    elif product_id:
        product = Product.objects.filter(pk=product_id).last()
    elif uuid:
        product = Product.objects.filter(oid=uuid).last()

    if not product:
        return restStatus(request, False, error="unknown product")
    if product.owner != request.member or (product.group and not request.member.isMemberOf(product.group)):
        if not request.user.is_staff:
            return restPermissionDenied(request)
        product.saveFromRequest(request, owner=request.member)
    return restGet(request, product, **Product.getGraph("default"))


@rd.urlGET (r'^product/(?P<product_id>\d+)$')
@rd.urlGET (r'^product/uuid/(?P<uuid>\w+)$')
@rd.login_optional
def getProduct(request, product_id=None, uuid=None):
    product = None
    if product_id:
        product = Product.objects.filter(pk=product_id).last()
    elif uuid:
        product = Product.objects.filter(oid=uuid).last()
    else:
        return restNotFound(request)

    if not product:
        return restStatus(request, False, error="unknown product")
    if not product.is_public and not request.member:
        return restPermissionDenied(request, "not logged in")
    return product.restGet(request)


@rd.urlGET (r'^product$')
@rd.login_optional
def listProducts(request):
    if not request.member:
        return restPermissionDenied(request)
    if not request.member.is_staff:
        return restPermissionDenied(request)

    kind = request.DATA.get("kind")
    qset = Product.objects.filter(archived=False)
    if kind:
        qset = qset.filter(kind=kind)

    return restList(request, qset, **Product.getGraph("default"))


@rd.urlPOST (r'^release$')
@rd.urlPOST (r'^release/(?P<release_id>\d+)$')
@rd.login_optional
def updateRelease(request, release_id=None):
    if not request.member:
        return restPermissionDenied(request)

    if not release_id:
        auto_version = request.DATA.get("auto_version", False)
        prod_uuid = request.DATA.get(["product", "product_uuid"])
        product = None
        if prod_uuid:
            product = Product.objects.filter(oid=prod_uuid).last()
        else:
            prod_id = request.DATA.get("product_id")
            if prod_id:
                product = Product.objects.filter(pk=prod_id).last()
        if not product:
            return restStatus(request, False, error="product required")
        version_num = request.DATA.get("version_num", field_type=int)
        last_release = Release.objects.filter(product=product).order_by("-version_num").first()

        if not version_num:
            if last_release and auto_version:
                version_num = last_release.version_num + 1
            elif auto_version:
                version_num = 1
            else:
                return restStatus(request, False, error="no version info supplied, try auto_version=1")
        elif last_release and version_num <= last_release.version_num:
            return restStatus(request, False, error="version is not greater then last")

        release = Release.createFromRequest(request, product=product, owner=request.member, group=request.group, version_num=version_num)
    else:
        release = Release.objects.filter(pk=release_id).last()
        if not release:
            return restStatus(request, False, error="unknown release")
        if release.owner != request.member or (release.product.group and not request.member.isMemberOf(release.product.group)):
            if not request.user.is_staff:
                return restPermissionDenied(request)
        release.saveFromRequest(request, owner=request.member)
    if request.DATA.get("make_current"):
        release.makeCurrent()
    elif request.DATA.get("make_beta"):
        release.makeCurrent()
    return restGet(request, release, **Release.getGraph("default"))


@rd.urlGET (r'^release/(?P<release_id>\d+)$')
@rd.login_optional
def getRelease(request, release_id):
    release = Release.objects.filter(pk=release_id).last()
    if not release:
        return restStatus(request, False, error="unknown release")
    if not release.product.is_public and not request.member:
        return restPermissionDenied(request, "not logged in")
    return restGet(request, release, **Release.getGraph("default"))


def reportRestIssue(subject, message, perm="rest_errors", email_only=False):
    # notifyWithPermission(perm, subject, message=None, template=None, context=None, email_only=False)
    # notify email only
    Member.notifyWithPermission(perm, subject, message, email_only=email_only)