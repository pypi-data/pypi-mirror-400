from rest import settings

DEBUG_REST_ALL = settings.get("DEBUG_REST_ALL", False)
DEBUG_REST_END_POINTS = settings.get("DEBUG_REST_END_POINTS", [])
IGNORE_REST_END_POINTS = settings.get("IGNORE_REST_END_POINTS", [])
LOG_REST_PREFIX = settings.get("REST_PREFIX", "api/")
if not LOG_REST_PREFIX.startswith("/"):
    LOG_REST_PREFIX = f"/{LOG_REST_PREFIX}"


def checkRestDebug(request):
    if checkRestIgnore(request):
        return False
    if DEBUG_REST_ALL:
        return True
    for ep in DEBUG_REST_END_POINTS:
        if request.path.startswith(ep):
            return True
    return False


def checkRestIgnore(request):
    for ep in IGNORE_REST_END_POINTS:
        if isinstance(ep, tuple):
            method, epath = ep
            if request.method == method and request.path.startswith(epath):
                return True
        if request.path.startswith(ep):
            return True
    return False


class LogRequest(object):
    last_request = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.process_request(request)

    def process_request(self, request):
        # LogRequest.last_request = request
        request.rest_debug = False
        if request.path.startswith(LOG_REST_PREFIX) or request.path.startswith("/rpc/"):
            request.rest_debug = checkRestDebug(request)
            if request.rest_debug:
                request.DATA.log()
        response = self.get_response(request)
        return response
