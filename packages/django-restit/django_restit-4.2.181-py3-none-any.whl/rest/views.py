from rest import settings
if settings.LEGACY_SERIALIZER:
    from .serializers.legacy import *  # noqa: F401, F403
else:
    from .serializers.response import *  # noqa: F401, F403
from . import url_docs
from django.shortcuts import render
REST_PREFIX = settings.get("REST_PREFIX", "api/")


def showDocs(request):
    from . import urls
    apis, graphs = url_docs.getRestApis(urls.urlpatterns)
    for api in apis:
        api["url"] = "{REST_PREFIX}{0}".format(api["url"])
    return render(request, "rest_docs.html", {"apis": apis, "graphs":graphs})


def __autoResponse(data, **kwargs):
    return '{"status": false, "error": "system offline"}'


backUpResult = restResult
_returnResults = restResult


def __offline(request):
    if settings.OFFLINE_KEY and request.get("key_check") == settings.OFFLINE_KEY:
        # remove failed files
        if request.DATA.get("offline", field_type=bool, default=1):
            restResult = __autoResponse
        else:
            restResult = backUpResult


def csrf_failure(request, reason=""):
    return restStatus(request, False, error=f"csrf failure: {reason}")
