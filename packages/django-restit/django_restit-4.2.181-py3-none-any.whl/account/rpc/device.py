from rest import decorators as rd
from rest import views as rv
from rest import helpers as rh
from account import models as am
from objict import objict


@rd.url(r'^group/cloud/credentials$')
@rd.url(r'^group/cloud/credentials/(?P<pk>\d+)$')
@rd.login_required
def rest_on_group_cloud_creds(request, pk=None):
    return am.CloudCredentials.on_rest_request(request, pk)


@rd.url(r'^member/device$')
@rd.url(r'^member/device/(?P<pk>\d+)$')
@rd.login_required
def rest_on_member_device(request, pk=None):
    return am.MemberDevice.on_rest_request(request, pk)


@rd.urlPOST('member/device/register')
@rd.login_required
def rest_on_member_device_register(request):
    # this requires a JWT with a device_id
    if not request.device_id:
        return rv.restPermissionDenied(request, "requires jwt with device id")
    md = am.MemberDevice.register(request, request.member, request.device_id)
    return rv.restStatus(request, md is not None)


@rd.urlPOST(r'^member/device/unregister$')
@rd.login_required
def rest_on_member_device_unregister(request):
    # this requires a JWT with a device_id
    if not request.device_id:
        return rv.restPermissionDenied(request, "requires jwt with device id")
    return rv.restStatus(request, am.MemberDevice.unregister(request.member, request.device_id))


@rd.urlPOST(r'^member/device/notify$')
@rd.login_required
def rest_on_member_device_notify(request):
    device_id, md = getMemberDevice(request)
    payload = request.DATA.get("payload")
    if payload is None:
        return rv.restPermissionDenied(request, error="missing payload")
    if md is None:
        return rv.restPermissionDenied(request, error=F"missing device: {device_id}")
    if payload.kind == "notification":
        r = md.sendNotification(payload.title, payload.body)
    else:
        r = md.sendData(payload)
    if r.status_code != 200:
        rh.log_error(payload, r.reason, r.status_code, r.text)
        return rv.restStatus(request, False, error=r.reason, code=r.status_code)
    return rv.restGet(request, r.json())


def getMemberDevice(request):
    device_id = request.DATA.get(["device_id", "deviceID", "device"])
    if not device_id:
        return None, None
    return device_id, am.MemberDevice.objects.filter(uuid=device_id).last()

