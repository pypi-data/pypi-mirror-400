from rest import decorators as rd
from .. import models as location


@rd.urlGET('ip')
def on_myip(request):
    gip = location.GeoIP.get(request.ip)
    graph = request.DATA.get("graph", "default")
    return gip.restGet(request, graph)


@rd.urlGET('ips')
def rest_on_geoip(request):
    return location.GeoIP.on_rest_list(request)


@rd.urlGET(r'^ip/lookup$')
def on_ip_lookup(request):
    ip = request.DATA.get("ip", request.ip)
    gip = location.GeoIP.get(
        ip,
        force_refresh=request.DATA.get("refresh", 0, field_type=bool),
        stale_after=request.DATA.get("stale_after", 90, field_type=int))
    graph = request.DATA.get("graph", "default")
    return gip.restGet(request, graph)


@rd.urlGET('geo/ip')
@rd.urlGET('geo/ip/<int:pk>')
def rest_on_geoip(request, pk=None):
    return location.GeoIP.on_rest_request(request, pk)


@rd.urlPOST('geo/ip/<int:pk>')
@rd.perm_required(["manage_location"])
def rest_save_geoip(request, pk=None):
    return location.GeoIP.on_rest_request(request, pk)


@rd.urlPOST('geo/ip')
@rd.login_required
@rd.requires_params(["ip"])
def rest_on_geoip_lookup(request, pk=None):
    ip = request.DATA.get("ip", request.ip)
    gip = location.GeoIP.get(
        ip,
        force_refresh=request.DATA.get("refresh", 0, field_type=bool),
        stale_after=request.DATA.get("stale_after", 90, field_type=int))
    graph = request.DATA.get("graph", "default")
    return gip.restGet(request, graph)
