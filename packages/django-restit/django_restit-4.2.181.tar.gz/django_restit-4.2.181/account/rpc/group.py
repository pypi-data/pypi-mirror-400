from rest import decorators as rd
from rest import views as rv
from rest import helpers as rh
from account.models import Group, Membership, Member, GroupFeed, MemberFeed


@rd.url(r'^group$')
@rd.url(r'^group/$')  # required for legacy support
@rd.url(r'^group/(?P<pk>\d+)$')
@rd.login_required
def rest_on_group(request, pk=None):
    return Group.on_rest_request(request, pk)


@rd.urlGET(r'^member/groups$')
@rd.login_required
def member_groups(request):
    member_id = request.DATA.get(["member", "member_id"], request.member.id)
    if not member_id:
        return rv.restPermissionDenied(request)
    member = Member.objects.filter(pk=member_id).last()
    return Group.on_rest_list(request, member.getGroups())


@rd.url(r'^group/invite$')
@rd.url(r'^group/invite/(?P<group_id>\d+)$')
@rd.perm_required(["manage_members", "invite_members", "manage_groups"])
def rest_on_group_invite(request, group_id=None):
    if group_id:
        group = Group.objects.filter(pk=group_id).first()
        if not group:
            return rv.restPermissionDenied(request)
    else:
        group = request.group
    if group is None:
        return rv.restPermissionDenied(request, "requires group")
    # this will throw exception on failure
    ms = None
    member = None
    member_id = request.DATA.get(["member", "member_id"])
    if member_id:
        member = Member.objects.filter(pk=member_id).last()
    if member is None:
        # create new member, but only allow basic information
        data = request.DATA.fromKeys(["username", "email", "phone_number", "display_name", "first_name", "last_name"])
        if not data or not data.email:
            return rv.restPermissionDenied(request, "missing fields")
        if data.email:
            member = Member.GetMember(data.email.lower().strip())
        elif data.username:
            member = Member.GetMember(data.username.lower().strip())
        elif data.phone_number:
            member = Member.GetMemberByPhone(data.phone_number)
        if member is None:
            member = Member.createFromDict(request, data)
        member.auditLog(f"created by {request.member.username}", "created", level=21)
    
    ms = Membership.objects.filter(member=member, group=group).first()
    if ms is None:
        member.auditLog(f"added to {group.name}:{group.id} by {request.member.username}", "group_invite", level=21)
        ms = group.invite(member, request.DATA.get("role", "guest"))
    elif not ms.is_enabled:
        # re-enable the member if they are being re-invited after being disabled
        if not ms.member.is_active:
            # we need to make sure we only enable the user for this group
            ms.member.enable(request.member, memberships=[], notify=False)
        ms.set_state(0)
        ms.save()
    ms.auditLog(f"invite sent by {request.member.username}", "invite", level=21)
    ms.sendInvite(request)
    return ms.restGet(request)


@rd.url(r'^membership$')
@rd.url(r'^membership/(?P<pk>\d+)$')
@rd.login_required
def rest_on_membership(request, pk=None):
    return Membership.on_rest_request(request, pk)


@rd.url(r'^membership/group/(?P<group_id>\d+)$')
@rd.url(r'^membership/me-(?P<group_id>\d+)$')
@rd.login_required
def rest_on_users_membership(request, group_id=None):
    ms = request.member.getMembershipFor(group_id, include_parents=True)
    if ms is None:
        return rv.restStatus(request, False, error="not found", error_code=404)
    if not ms.is_enabled:
        return rv.restPermissionDenied(
            request,
            error=f"membership({request.member.username}) has been disabled for this group({group_id})",
            error_code=410)
    return ms.restGet(request)


@rd.url('group/feed')
@rd.url('group/feed/<int:pk>')
@rd.login_required
def rest_on_group_feed(request, pk=None):
    return GroupFeed.on_rest_request(request, pk)


@rd.urlGET('member/feed')
@rd.urlGET('member/feed/<int:pk>')
@rd.login_required
def rest_on_member_feed(request, pk=None):
    return MemberFeed.on_rest_request(request, pk)


@rd.urlGET('group/stats/kinds')
@rd.login_required
def rest_on_group_stats(request):
    params = request.DATA.asDict()
    if not params.group:
        if not request.member.hasPerm(["view_all_groups", "manage_groups"]):
            return rv.restPermissionDenied()
        out = rh.countOccurences(Group.objects.filter(is_active=True), "kind")
        return rv.restResult(request, dict(data=out))
    # local
    group = Group.objects.filter(pk=params.group).first()
    if not group:
        return rv.restPermissionDenied(request)
    if not request.member.hasPerm(["view_all_groups", "manage_groups"]):
        if not request.member.hasGroupPerm(group, ["reports", "reporting"]):
            return rv.restPermissionDenied(request)
    qset = group.getAllChildren(True, True, True).filter(is_active=True)
    out = rh.countOccurences(qset, "kind")
    return rv.restResult(request, dict(data=out))
    
