from rest import decorators as rd
from rest import views as rv
from rest import helpers as rh
from rest import settings
from . import models as am 
from .parsers import ossec
from taskqueue.models import Task
from location.providers.iplookup import abuse
import incident
from objict import objict

LOG_REST_PREFIX = settings.get("REST_PREFIX", "api/")
if not LOG_REST_PREFIX.startswith("/"):
    LOG_REST_PREFIX = f"/{LOG_REST_PREFIX}"
STATUS_ON_PERM_DENIED = settings.get("STATUS_ON_PERM_DENIED", 403)


def patched_restPermissionDenied(request, error="permission denied", 
                                 error_code=403, status=STATUS_ON_PERM_DENIED,
                                 component=None, component_id=None):
    
    description = f"permission denied: {error_code} '{error}' for {request.user} {request.method}:{request.path}"
    # rh.log_error(description)
    if error_code == 404:
        if not request.path.startswith(LOG_REST_PREFIX) and not request.path.startswith("/rpc"):
            # just ignore these
            return rv.restResult(request, dict(status=False, error=error, error_code=error_code), status=status)

    metadata = dict(error=error, error_code=error_code, details=description)
    if component is not None:
        metadata["component"] = component
        metadata["component_id"] = component_id
    if hasattr(request, "member") and request.member is not None:
        request.DATA.log()
        request.member.log("rest_denied", error, request, level=10)
        if component is None:
            metadata["component"] = "account.Member"
            metadata["component_id"] = request.member.pk

    if getattr(request, "token_bearer", None) is not None:
        metadata["token_bearer"] = request.token_bearer
        metadata["token"] = f"***{request.token[-6:]}"
    incident.event_now(
        "rest_denied",
        description,
        level=10,
        request=request,
        **metadata)
    return rv.restResult(request, dict(status=False, error=error, error_code=error_code), status=status)


def patched_restNotFound(request):
    return rv.restPermissionDenied(request, error="not found", error_code=404)


if settings.REPORT_PERMISSION_DENIED:
    rv.restPermissionDenied = patched_restPermissionDenied


@rd.urlPOST(r'^ossec/alert/batch$')
def batch_ossec_alert_creat_from_request(request):
    batch = request.DATA.get("batch")
    if isinstance(batch, str):
        batch = objict.fromJSON(batch)
    if not isinstance(batch, list):
        rh.debug("ossec batch data", batch)
        rh.debug("ossec data", request.DATA.asDict())
        data_format = str(type(batch))
        return rv.restStatus(request, False, error=f"invalid format {data_format}")
    for alert in batch:
        on_ossec_alert(request, alert)
    return rv.restStatus(request, True)  


@rd.urlPOST(r'^ossec/alert$')
def ossec_alert_creat_from_request(request):
    payload = request.DATA.get("payload")
    if not payload:
        return rv.restStatus(request, False, error="no alert data")
    on_ossec_alert(request, payload)
    return rv.restStatus(request, True)


def on_ossec_alert(request, alert):
    try:
        # TODO make this a task (background it)
        # rh.log_error("parsing payload", payload)
        od = ossec.parseAlert(request, alert)
        # lets now create a local event
        if od is not None:
            level = 10
            if od.level > 10:
                level = 1
            elif od.level > 7:
                level = 2
            elif od.level == 6:
                level = 3
            elif od.level == 5:
                level = 4
            elif od.level == 4:
                level = 6
            elif od.level <= 3:
                level = 8
            metadata = od.toDict(graph="default")
            metadata.update(od.metadata)
            # we reuse the ssh_sig because it is a text field to store urls
            # ssh_sig = metadata.get("ssh_sig", None)
            # if ssh_sig is not None and ssh_sig.startswith("http"):    
            #     metadata["url"] = ssh_sig
            #     metadata["domain"] = ossec.extractDomain(ssh_sig)
            #     metadata["path"] = ossec.extractUrlPath(ssh_sig)
            #     metadata.pop("ssh_sig")
            if od.geoip:
                metadata["country"] = od.geoip.country
                metadata["city"] = od.geoip.city
                metadata["province"] = od.geoip.state
                metadata["isp"] = od.geoip.isp

            evt = am.Event.createFromDict(None, {
                "hostname": od.hostname,
                "description": od.title,
                "details": od.text,
                "level": level,
                "category": "ossec",
                "component": "incident.ServerOssecAlert",
                "component_id": od.id,
                "reporter_ip": od.src_ip,
                "metadata": metadata
            })
            # fix the created datetime to be from when it was actually happening
            evt.created = od.when
            evt.save()
            return rv.restStatus(request, True)
    except Exception as err:
        rh.log_exception()
        stack = rh.getStackString()
        # rh.log_exception("during ossec alert", payload)
        metadata = dict(ip=request.ip, payload=alert)
        am.Event.createFromDict(None, {
            "hostname": request.get_host(),
            "description": f"error parseing alert: {err}",
            "details": stack,
            "level": 8,
            "category": "ossec_error",
            "metadata": metadata
        })
    # rh.log_error("ossec alert", request.DATA.asDict())
    return rv.restStatus(request, False, error="no alert data")


@rd.urlGET(r'^ossec$')
@rd.urlGET(r'^ossec/(?P<pk>\d+)$')
@rd.login_required
def on_ossec(request, pk=None):
    return am.ServerOssecAlert.on_rest_request(request, pk)


@rd.urlPOST(r'^event$')
def rest_on_create_event(request, pk=None):
    # TODO check for key?
    resp = am.Event.on_rest_request(request)
    return rv.restStatus(request, True)


@rd.urlGET(r'^event$')
@rd.urlGET(r'^event/(?P<pk>\d+)$')
@rd.urlPOST(r'^event/(?P<pk>\d+)$')
@rd.login_required
def rest_on_event(request, pk=None):
    return am.Event.on_rest_request(request, pk)


@rd.url(r'^incident$')
@rd.url(r'^incident/(?P<pk>\d+)$')
@rd.login_required
def rest_on_incident(request, pk=None):
    return am.Incident.on_rest_request(request, pk)


@rd.url(r'^incident/history$')
@rd.url(r'^incident/history/(?P<pk>\d+)$')
@rd.login_required
def rest_on_incident_history(request, pk=None):
    return am.IncidentHistory.on_rest_request(request, pk)


@rd.url(r'^rule$')
@rd.url(r'^rule/(?P<pk>\d+)$')
@rd.login_required
def rest_on_rule(request, pk=None):
    return am.Rule.on_rest_request(request, pk)


@rd.url(r'^rule/check$')
@rd.url(r'^rule/check/(?P<pk>\d+)$')
@rd.login_required
def rest_on_rule_check(request, pk=None):
    return am.RuleCheck.on_rest_request(request, pk)


# BEGIN FIREWALL
@rd.urlPOST(r'^ossec/firewall$')
def ossec_firewall_event(request):
    data = request.DATA.toObject()
    # rh.debug("firewall event", data)
    gip = ossec.GeoIP.lookup(data.ip)
    if gip:
        data.country = gip.country
        data.province = gip.state
        data.city = gip.city
        data.isp = gip.isp
        data.ip_hostname = gip.hostname
    if data.action == "add":
        data.action = "blocked"
    else:
        data.action = "unblocked"
    record_block(data.ip, data.action, data.hostname, data)
    # now block the ip globally
    if settings.FIREWALL_GLOBAL_BLOCK:
        Task.Publish("incident", "firewall_block", dict(ip=data.ip), channel="tq_broadcast")
    return rv.restStatus(request, True)


def record_block(ip, action, hostname, metadata):
    title = f"FIREWALL: {ip} {action} on {hostname}"
    am.Event.createFromDict(None, dict(
        hostname=hostname,
        reporter_ip=ip,
        description=title,
        details=title,
        category="firewall",
        level=6,
        metadata=metadata
    ))


@rd.urlGET(r'^firewall$')
# @rd.superuser_required
def rest_firewall_blocked(request, pk=None):
    return rv.restReturn(request, dict(data=dict(blocked=rh.getBlockedHosts())))


@rd.urlPOST(r'^firewall$')
@rd.superuser_required
@rd.requires_params(["ip", "action"])
def rest_firewall_block(request):
    # block the ip globally
    ip = request.DATA.get("ip")
    action = request.DATA.get("action")
    if action not in ["block", "unblock"]:
        return rv.restPermissionDenied(request)
    metadata = request.DATA.asDict()
    metadata.username = request.member.username
    record_block(ip, action, "all", metadata)
    Task.Publish("incident", f"firewall_{action}", dict(ip=ip), channel="tq_firewall")
    return rv.restStatus(request, True)


@rd.url('ticket')
@rd.url('ticket/<int:pk>')
def rest_on_ticket(request, pk=None):
    return am.Ticket.on_rest_request(request, pk)


@rd.urlGET('abuse/lookup')
@rd.requires_params(["ip"])
def rest_on_abuse_ip_lookup(request):
    resp = abuse.lookup(request.DATA.get("ip"), request.DATA.get("max_age", 0))
    return rv.restReturn(request, resp)


@rd.urlPOST('abuse/report')
@rd.requires_params(["ip", "comment", "categories"])
def rest_on_report_abuse(request):
    resp = abuse.reportAbuse(
        ip=request.DATA.get("ip"),
        comment=request.DATA.get("comment"),
        categories=request.DATA.get("categories"))
    return rv.restReturn(request, resp)
