from . import views

import version
from . import joke
from . import helpers

import django
from django.conf import settings


from .decorators import url
from rest.extra import hostinfo
from ws4redis import client as redis
from django.db import connections


URL_PREFIX = ""

SOFTWARE_VERSIONS = getattr(settings, 'SOFTWARE_VERSIONS', None)
ALLOW_PUBLIC_SYS_INFO = getattr(settings, 'ALLOW_PUBLIC_SYS_INFO', False)
SYS_INFO_KEY = getattr(settings, 'SYS_INFO_KEY', None)
# SOFTWARE_VERSIONS_ACTUAL = {}


@url('version')
def on_get_version(request):
    return views.restStatus(request, True, {"data": version.VERSION, "ip": request.ip})


@url('versions')
def on_get_version(request):
    from rest import __version__ as restit_version
    versions = dict(
        project=version.VERSION,
        restit=restit_version)
    if request.DATA.get("detailed") and SOFTWARE_VERSIONS:
        hostinfo.getVersions(versions)
    return views.restStatus(request, True, {"data": versions})


@url('test/session')
def on_get_my_session(request):
    echo = request.DATA.get("echo", None)
    if echo:
        request.session["echo"] = echo
    return views.restReturn(request, dict(echo=request.session.get("echo", "not set")))


@url('joke')
def on_get_joke(request):
    return views.restGet(request, {"joke": joke.getRandomJoke()})


@url('status')
def on_get_status(request):
    flag = True
    try:
        flag = redis.ping()
    except Exception:
        flag = False
    status = dict(redis=flag, database={}, pool=redis.getPoolStatus())
    for alias in settings.DATABASES.keys():
        db_conn = connections[alias]
        try:
            # Ensure connection with a timeout
            db_conn.ensure_connection()
            status["database"][alias] = True
        except Exception:
            flag = False
            status["database"][alias] = False
    if flag:
        return views.restGet(request, status)
    return views.restResult(request, status, 417)

@url('system/info')
def on_get_system_info(request):
    key = request.DATA.get("key")
    if SYS_INFO_KEY is None or key != SYS_INFO_KEY:
        if not ALLOW_PUBLIC_SYS_INFO and not request.user.is_authenticated:
            return views.restPermissionDenied(request, "system info is not public", 565)
    out = hostinfo.getHostInfo(
        include_versions=request.DATA.get("versions") and SOFTWARE_VERSIONS,
        include_blocked=request.DATA.get("blocked"))
    out["redis_pool"] = redis.getPoolStatus()
    return views.restGet(request, out)


@url('system/cons')
def on_get_system_cons(request):
    key = request.DATA.get("key")
    if SYS_INFO_KEY is None or key != SYS_INFO_KEY:
        if not ALLOW_PUBLIC_SYS_INFO and not request.user.is_authenticated:
            return views.restPermissionDenied(request, "system info is not public", 565)
    cons = hostinfo.getTcpEstablished(filter=request.DATA.get("filter"))
    return views.restList(request, hostinfo.consToDict(cons))

