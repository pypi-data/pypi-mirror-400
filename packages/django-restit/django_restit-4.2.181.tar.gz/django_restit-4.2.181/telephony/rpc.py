from django.db import models
from django.conf import settings
from django.http import HttpResponse

from telephony.models import SMS, PhonenumberInfo
from account import models as am
from rest import helpers
from rest import views as rv
from rest import decorators as rd
import importlib

try:
    from twilio.twiml.messaging_response import MessagingResponse
except ImportError:
    pass


@rd.url('sms/msg')
@rd.url('sms/msg/<int:pk>')
def handle_sms_list(request, pk=None):
    return SMS.on_rest_request(request, pk)


@rd.urlGET('info')
@rd.urlGET('info/<int:pk>')
def handle_number_info(request, pk=None):
    return PhonenumberInfo.on_rest_request(request, pk)


@rd.urlPOST('info')
@rd.login_required
@rd.requires_params(["phone_number"])
def handle_number_lookup(request, pk=None):
    number = request.DATA.get("phone_number")
    info = PhonenumberInfo.lookup(number)
    if info.pk is None:
        return rv.restStatus(request, False, error="Invalid number")
    return info.restGet(request)


@rd.urlPOST(r'^sms$')
@rd.urlPOST(r'^sms/$')
@rd.login_required
def sendSMS(request):
    me = request.member
    group = request.group
    # for now you can only send msgs to a member
    if "to" in request.DATA:
        to = request.DATA.getlist("to")
        members = am.Member.objects.filter(pk__in=to)
        message = request.DATA.get("message")
        return rv.restGet(request, SMS.broadcast(members, message, by=me, group=group, transport="sms"))

    if "message" not in request.DATA:
        return rv.restStatus(request, False, error="permission denied")

    member = am.Member.getFromRequest(request)
    if not member:
        return rv.restStatus(request, False, error="requires valid member")
    phone = member.getProperty("phone")
    if not phone:
        return rv.restStatus(request, False, error="member has no phone number")
    message = request.DATA.get("message")
    # send(endpoint, message, by=None, group=None, to=None, transport="sms", srcpoint=None):
    return rv.restGet(request, SMS.send(phone, message, me, group, member))


@rd.urlPOST(r'^sms/incoming$')
def receiveSMS(request):
    helpers.log_print(request.DATA.asDict())
    SMS.log_incoming(request)
    from_number = request.DATA.get("From")
    handler_name = settings.TELEPHONY_HANDLERS.get(from_number, None)
    if handler_name is not None:
        model = importlib.import_module(handler_name)
        msg = model.on_sms(request)
        if msg is not None:
            resp = MessagingResponse()
            resp.message(msg)
            return HttpResponse(resp.to_xml(), content_type='text/xml')
    resp = MessagingResponse()
    resp.message(settings.TELEPHONY_DEFAULT_SMS_RESPONSE)
    return HttpResponse(resp.to_xml(), content_type='text/xml')


@rd.url(r'^lookup$')
@rd.login_required
def handle_lookup(request, pk=None):
    number = request.DATA.get(["number", "phone"])
    if number is None:
        return rv.restPermissionDenied(request)
    info = PhonenumberInfo.lookup(number)
    return info.restGet(request)


@rd.urlPOST('sms/twilio/status')
def handle_twilio_status(request, pk=None):
    sid = request.DATA.get("MessageSid", None)
    msd = None
    if sid is not None:
        msg = SMS.objects.filter(sid=sid).last()
        if msg is not None:
            msg.status = request.DATA.get("MessageStatus", None)
            msg.reason = request.DATA.get("ErrorCode", None)
            msg.save()
    return rv.restSuccessNoContent(request)

