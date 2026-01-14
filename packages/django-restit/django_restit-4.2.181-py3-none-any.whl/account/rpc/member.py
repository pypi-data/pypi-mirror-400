from rest import decorators as rd
from rest.views import restPermissionDenied, restStatus, restHTML
from rest import helpers as rh
from account import models as am


@rd.url(r'^member$')
@rd.url(r'^member/$')
@rd.url(r'^member/(?P<pk>\d+)$')
@rd.login_required
def rest_on_member(request, pk=None):
    return am.Member.on_rest_request(request, pk)


@rd.urlPOST('member/motd/reset')
@rd.perm_required('manage_members')
def rest_on_clear_motd(request):
    key = request.DATA.get("key")
    if key.startswith("viewed."):
        key = key.split('.')[-1]
        am.MemberMetaData.objects.filter(key=key, category="viewed").delete()
    else:
        am.MemberMetaData.objects.filter(key="saw_motd", category__isnull=True).delete()
    return restStatus(request, True)


@rd.url(r'^member/me$')
@rd.login_optional
def member_me_action(request):
    if not request.user.is_authenticated:
        return restPermissionDenied(request, "not authenticated")
    if request.method == "GET":
        # request.session['ws4redis:memberof'] = request.member.getGroupUUIDs()
        # from rest import helpers as rh
        # rh.debug("user_platform", request.DATA.getUserAgentPlatform())
        return request.member.on_rest_get(request)
    elif request.method == "POST":
        return request.member.on_rest_post(request)
    return restStatus(request, False, error="not supported")


@rd.url(r'^authtoken$')
@rd.url(r'^authtoken/(?P<pk>\d+)$')
@rd.login_required
def rest_on_authtoken(request, pk=None):
    return am.AuthToken.on_rest_request(request, pk)


@rd.url(r'^session$')
@rd.url(r'^session/(?P<pk>\d+)$')
@rd.login_required
def rest_on_session(request, pk=None):
    return am.AuthSession.on_rest_request(request, pk)


@rd.urlGET('unsubscribe')
@rd.requires_params(["t"])
def rest_on_member(request):
    t = request.DATA.get("t")
    m = am.Member.objects.filter(uuid=t).last()
    if m is not None:
        m.addPermission("email_disabled")
        m.reportIncident("email", f"{m.email} has unsubscribed to all email")
    context = rh.getContext(request, member=m)
    if request.DATA.get("format") == "json":
        return restStatus(request, True)
    return restHTML(request, template="unsubscribed.html", context=context)
