from django.db import models
from django.db.models import Q
import re

from rest.models import RestModel, MetaDataModel, MetaDataBase, RestValidationError, PermissionDeniedException
from rest import helpers as rh
from rest import RemoteEvents
from rest import crypto
from rest import mail as rest_mail
from rest.views import restPermissionDenied

from .member import Member

from rest import settings
app_settings = settings.getAppSettings("account")
MEMBERSHIP_ROLES = settings.get("MEMBERSHIP_ROLES", None)
TRUE_VALUES = app_settings.get("TRUE_VALUES", [])


class Group(models.Model, RestModel, MetaDataModel):
    """
    Group Model allows for the grouping of other models and works with Member throug Membership Model

    parent allows for tree based heirachy of groups
    children allows for manytomany relationships with other groups
    kind is heavily used to filter different kinds of groups
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    uuid = models.CharField(db_index=True, max_length=64, blank=True, null=True, default=None)
    name = models.CharField(db_index=True, max_length=200)
    short_name = models.CharField(max_length=60, null=True, blank=True, default=None)
    kind = models.CharField(db_index=True, max_length=80, default="org")
    parent = models.ForeignKey("Group", default=None, null=True, blank=True, related_name="groups", on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True, blank=True)
    # this is the new model for groups having multiple parents
    children = models.ManyToManyField("self", related_name="parents", symmetrical=False)

    location = models.ForeignKey(
        "location.Address", default=None, null=True, blank=True,
        related_name="+", on_delete=models.SET_NULL)

    class RestMeta:
        SEARCH_FIELDS = [
            "name"
        ]
        LIST_DEFAULT_FILTERS = {
            "is_active": True
        }
        LIST_PARENT_KINDS = ["org", "iso"]
        POST_SAVE_FIELDS = ["child_of"]
        GROUP_FIELD = "self"
        CAN_BATCH = True
        VIEW_PERMS = [
            "view_all_groups",
            "manage_groups",
            "manage_group",
            "manage_settings"]
        SAVE_PERMS = [
            "manage_groups",
            "manage_group",
            "manage_settings"]
        CREATE_PERMS = ["manage_groups", "create_groups"]
        GRAPHS = {
            "basic": {
                "fields": [
                    "id",
                    "parent",
                    "uuid",
                    "name",
                    "short_name",
                    "kind",
                    "created",
                    "thumbnail",
                    "is_active",
                    "timezone"
                ]
            },
            "default": {
                "graphs": {
                    "self": "basic",
                    "parent": "basic",
                    "location": "basic"
                },
                "fields": ["metadata"],
            },
            "detailed": {
                "graphs": {
                    "self": "basic",
                    "parent": "basic",
                    "children": "basic",
                    "location": "basic"
                },
                "extra": ["metadata"],
            },
            "location": {
                "fields": ["name", "kind", "id"],
                "extra": ["location"],
                "graphs": {
                    "location": "basic"
                }
            },
            "abstract": {
                "fields": [
                    ('uuid', 'id'),
                    "name",
                    "kind",
                    "timezone"
                ]
            }
        }
        FORMATS = {
            "csv": [
                "created",
                "id",
                "name",
                "kind",
                ("metadata__timezone", "timezone"),
                ("metadata__eod", "end_of_day"),
                ("parent__pk", "parent_id"),
                ("parent__name", "parent"),
                ("location.line1", "address_line1"),
                ("location.line2", "address_line2"),
                ("location.city", "city"),
                ("location.state", "state"),
                ("location.county", "county"),
                ("location.country", "country"),
                ("location.postalcode", "zipcode"),
                ("location.postalcode_suffix", "zipcode_ext"),
                ("location.lat", "lat"),
                ("location.lng", "lng")
            ]
        }

    _tz_long = None
    _tz_short = None
    _eod_hour = None

    @property
    def timezone(self):
        if self._tz_long is None:
            self._tz_long = self.getParentProperty("timezone", "America/Los_Angeles")
        return self._tz_long

    @property
    def timezone_short(self):
        if self._tz_short is None:
            self._tz_short = rh.getShortTZ(self.timezone)
        return self._tz_short

    @property
    def end_of_day_hour(self):
        if self._eod_hour is None:
            self._eod_hour = self.getParentProperty("eod", 0, field_type=int)
        return self._eod_hour

    @property
    def file_safe_name(self):
        return re.sub("[^0-9a-zA-Z]+", "_", self.name.lower())

    @property
    def initials(self):
        if self.name:
            return "".join([s[0] for s in self.name.split(' ')]).upper()
        return None

    def thumbnail(self, name="default"):
        lib = self.libraries.filter(name=name).first()
        if lib:
            item = lib.items.all().first()
            if item:
                return item.thumbnail_url()
        return None

    @classmethod
    def on_rest_list_filter(cls, request, qset=None):
        if not request.member.hasPermission("view_all_groups"):
            qset = request.member.getGroups()
        # override on do any pre filters
        child_of = request.DATA.get("child_of")
        if request.group is not None and child_of is None:
            child_of = request.group.id
        parent_id = request.DATA.get(["parent", "parent_id"])
        if parent_id:
            parent = request.member.getGroup(parent_id)
            if not parent:
                raise PermissionDeniedException("invalid parent")
            qset = qset.filter(parent=parent)
        elif child_of:
            parent = request.member.getGroup(child_of)
            if parent:
                request.group = None
                return parent.getAllChildren(grand_children=True, great_grand_children=True)
        return qset

    def on_rest_get(self, request):
        if (request.member and request.member.isMemberOf(self)) or self.on_rest_can_get(request):
            return self.restGet(request)
        return restPermissionDenied(request)

    # def onRestCanSave(self, request=None, data=None, extended=None):
    #     if request.member is None:
    #         raise PermissionDeniedException("permission denied for save")
    #     if request.member.hasPermission(["manage_groups", "create_groups"]):
    #         return True
    #     if self.checkPermission(request.member, ["manage_settings", "manage_members", "manage_group"]):
    #         return True
    #     raise PermissionDeniedException("permission denied for save")

    def on_rest_pre_save(self, request, **kwargs):
        pass

    def on_rest_saved(self, request, is_new=False):
        if request.member:
            note = "edited group {}:{}\n{}".format(self.name, self.pk, request.DATA.asDict())
            request.member.log("group_edit", note, method="group")
            self.auditLog(note, "group_edit", level=21)
            self.logEvent("group_edit", component="account.Member", component_id=request.member.id, note=note)

    def set_name(self, value):
        if value is not None:
            self.name = value.strip()
        else:
            self.name = None

    def set_parent(self, value):
        if not value:
            value = None
        else:
            if int(value) == self.pk:
                raise RestValidationError("cannot set self as parent", 1101)
            value = Group.objects.filter(pk=value).last()
        self.parent = value

    def set_child_of(self, value):
        # this is a helper to add this group to another group
        parent = Group.objects.filter(pk=value).last()
        if parent and parent.pk != self.pk:
            if not parent.children.filter(pk=self.pk).exists() and not self.hasChild(parent) and self.kind != "org":
                parent.children.add(self)

    def set_remove_parent(self, value):
        parent = Group.objects.filter(pk=value).last()
        if parent:
            if parent.children.filter(pk=self.pk).exists():
                parent.children.remove(self)

    def set_timezone(self, value):
        if self.pk:
            self._tz_long = None
            self._tz_short = None
            self.setProperty("timezone", value)

    def getChildModels(self, Model, grand_children=False, great_grand_children=False):
        q = Q(group=self)
        if grand_children:
            q = q | Q(group__parent=self)
        if great_grand_children:
            q = q | Q(group__parent__parent=self)
            q = q | Q(group__parent__parent__parent=self)
        if hasattr(Model, "objects"):
            return Model.objects.filter(q)
        return Model.filter(q)

    def getChildren(self):
        return Group.objects.filter(parent=self)

    def getAllChildren(self, include_me=False, grand_children=False, great_grand_children=False):
        q = Q(parent=self)| Q(parents=self)
        if include_me:
            q = q | Q(pk=self.id)
        if grand_children:
            q = q | Q(parent__parent=self)
        if great_grand_children:
            q = q | Q(parent__parent__parent=self)
            q = q | Q(parent__parent__parent__parent=self)
        return Group.objects.filter(q)

    def getAllChildrenIds(self, include_me=False, grand_children=False, great_grand_children=False, depth=0):
        if depth > 1:
            grand_children = True
        if depth > 2:
            great_grand_children = True
        qset = self.getAllChildren(include_me, grand_children, great_grand_children)
        return list(qset.values_list("id", flat=True))

    def hasChild(self, group):
        if not group:
            return False
        if self.children.filter(pk=group.pk).exists():
            return True
        for child in self.children.all():
            if child.hasChild(group):
                return True
        return False

    def getParentOfKind(self, kind):
        if self.parent:
            if self.parent.kind == kind:
                return self.parent
            parent = self.parent.getParentOfKind(kind)
            if parent:
                return parent
        group = self.parents.filter(kind=kind).first()
        if group:
            return group
        for parent in self.parents.all():
            if parent.kind == kind:
                return parent
            group = parent.getParentOfKind(kind)
            if group:
                return group
        return None

    def hasParent(self, group):
        # this needs to check parents...then check each parent for parent
        if self.parent:
            if self.parent == group:
                return True
            if self.parent.hasParent(group):
                return True
        if self.parents.filter(pk=group.id).count():
            return True
        for parent in self.parents.all():
            if parent == group:
                return True
            if parent.hasParent(group):
                return True
        return False

    def notifyMembers(self, subject, message=None, template=None, context=None,
                      email_only=False, sms_msg=None, perms=None, force=False,
                      from_email=None, exclude_member=None):
        if perms is not None:
            members = self.getMembers(perms=perms, as_member=True, exclude_member=exclude_member)
        else:
            Member = RestModel.getModel("account", "Member")
            members = Member.objects.filter(
                is_active=True, memberships__group=self,
                memberships__state__gte=-10)
            if exclude_member:
                members = members.exclude(pk=exclude_member.pk)
        NotificationRecord = RestModel.getModel("account", "NotificationRecord")
        NotificationRecord.notify(
            members, subject, message, template,
            context, email_only, sms_msg, force,
            from_email=from_email)

    def hasPerm(self, member, perm, staff_override=True, check_member=False):
        return self.checkPermission(member, perm, staff_override, check_member)

    def checkPermission(self, member, perm, staff_override=True, check_member=False):
        if member.is_superuser:
            return True
        if staff_override and member.is_staff:
            return True
        if check_member:
            if member.hasPerm(perm) or member.hasGroupPerm(self, perm):
                return True
        memberships = member.memberships.filter(group=self)
        for ms in memberships:
            if ms.hasPermission(perm):
                return True
        return False

    def getParentProperty(self, key, default=None, category=None, field_type=None, decrypted=False):
        val = self.getProperty(key, rh.UNKNOWN, category, field_type, decrypted)
        if val != rh.UNKNOWN:
            return val
        if self.parent:
            val = self.parent.getProperty(key, rh.UNKNOWN, category, field_type, decrypted)
            if val != rh.UNKNOWN:
                return val
            return self.parent.getParentProperty(key, default, category, field_type, decrypted)
        return default

    def getLocalTime(self, when=None, tz_aware=False):
        return rh.convertToLocalTime(self.timezone, when, tz_aware)

    def getUTC(self, when):
        return rh.convertToUTC(self.timezone, when)

    def getBusinessDay(self, start=None, end=None, kind="day"):
        return rh.getDateRange(start, end, kind, self.timezone, hour=self.end_of_day_hour)

    def getOperatingHours(self, start=None, end=None, kind="day"):
        # deprecate this, operating hours is deceptive
        return rh.getDateRange(start, end, kind, self.timezone, hour=self.end_of_day_hour)

    def getTimeZoneOffset(self, when=None, hour=None):
        return rh.getTimeZoneOffset(self.timezone, when, hour=hour)

    def getEOD(self, eod=None, onday=None, in_local=False):
        if eod is None:
            eod = self.end_of_day_hour
            if in_local:
                return eod
        offset = self.getTimeZoneOffset(onday, hour=self.end_of_day_hour)
        return offset

    def updateUUID(self):
        self.uuid = crypto.obfuscateID("group", self.id)
        self.save()

    def isMember(self, member):
        return self.memberships.filter(member=member, state__gte=-10).count()

    def hasMember(self, member):
        return self.isMember(member)

    def addMember(self, member, role):
        return self.addMembership(member, role)

    def addMembership(self, member, role):
        if self.memberships.filter(member=member, role=role).count():
            return None
        Membership = RestModel.getModel("account", "Membership")
        ms = Membership(group=self, member=member, role=role)
        ms.save()
        return ms

    def getMembers(self, perms=None, role=None, as_member=False, exclude_member=None):
        if isinstance(perms, str):
            perms = [perms]
        if isinstance(role, str):
            role = [role]
        notify = None
        if perms:
            notify = [p.split('.')[1] for p in perms if p.startswith("notify.")]
            perms = [p for p in perms if not p.startswith("notify.")]
        if as_member:
            Member = RestModel.getModel("account", "Member")
            qset = Member.objects.filter(is_active=True, memberships__group=self, memberships__state__gte=-10)
            if perms:
                qset = qset.filter(memberships__group=self, memberships__properties__category="permissions", memberships__properties__key__in=perms, memberships__properties__value__in=TRUE_VALUES)
            if notify:
                qset = qset.filter(memberships__group=self, memberships__properties__category="notify", memberships__properties__key__in=notify, memberships__properties__value__in=TRUE_VALUES)
            if role:
                qset = qset.filter(memberships__group=self, memberships__role__in=role)
            if exclude_member:
                qset = qset.exclude(pk=exclude_member.pk)
            return qset.distinct()
        qset = self.memberships.filter(state__gte=-10)
        if perms:
            qset = qset.filter(
                Q(properties__category="permissions",
                  properties__key__in=perms,
                  properties__value__in=TRUE_VALUES) |
                Q(member__properties__category="permissions",
                  member__properties__key__in=perms,
                  member__properties__value__in=TRUE_VALUES))
        if notify:
            qset = qset.filter(
                Q(properties__category="notify",
                  properties__key__in=notify,
                  properties__value__in=TRUE_VALUES) |
                Q(member__properties__category="notify",
                  member__properties__key__in=notify,
                  member__properties__value__in=TRUE_VALUES))

        if role:
            qset = qset.filter(role__in=role)
        if exclude_member:
            qset = qset.exclude(member__pk=exclude_member.pk)
        return qset.distinct()

    def getParentIDs(self):
        ids = []
        group = self
        counter = 0
        while group.parent != None and counter < 6:
            counter += 1
            ids.append(group.parent.id)
            group = group.parent
        return ids

    def getMembership(self, member, include_parents=False):
        ms = self.memberships.filter(member=member).first()
        if ms or not include_parents:
            return ms
        group = self
        counter = 0
        while group.parent != None and counter < 6:
            counter += 1
            group = group.parent
            ms = group.getMembership(member)
            if ms:
                return ms
        return ms

    def invite(self, member, role="guest"):
        # invite a user to this group
        Membership = RestModel.getModel("account", "Membership")
        ms = Membership.objects.filter(group=self, member=member).last()
        if ms is None:
            ms = Membership(member=member, group=self, role=role)
            ms.save()
            ms.on_rest_created(self.getActiveRequest())
        elif ms.role != role:
            ms.clearPermissions()
        if not ms.is_enabled:
            # enable again?
            ms.set_state(0)
            ms.save()

        if MEMBERSHIP_ROLES:
            perms = MEMBERSHIP_ROLES.get(role, [])
            for k in perms:
                ms.setProperty(k, 1, category="permissions")
        return ms

    def getEmails(self, role=None, perms=None, master_perm=None):
        emails = []
        members = self.getMembers(role=role, perms=perms, as_member=True)
        for m in members:
            if "invalid" in m.email:
                continue
            emails.append(m.email)
        if master_perm:
            emails = emails + Member.GetWithPermission(master_perm, email_list=True)
        return emails

    def sendEmail(self, role=None, perms=None, subject="Notification", template="email/base", body="", context={}, master_perm=None):
        c = {
            'settings': settings,
            'subject': subject,
            'from': settings.get("DEFAULT_FROM_EMAIL"),
            "body": body,
            'group': self,
            'sent_to': None,
        }
        sent_to = []
        c.update(context)
        members = self.getMembers(role=role, perms=perms, as_member=True)
        for m in members:
            if "invalid" in m.email:
                continue
            # print m.email
            c["to"] = m.email
            sent_to.append(m.email)
            c["user"] = m
            rest_mail.render_to_mail(template, c)

        if master_perm:
            c["to"] = Member.GetWithPermission(master_perm, email_list=True)
            c["sent_to"] = c["to"]
            if c["to"]:
                rest_mail.render_to_mail(template, c)

    def sendEvent(self, name, message, custom=None):
        if not custom:
            custom = {}
        custom["group_id"] = self.id
        RemoteEvents.sendToGroup(
            self,
            name,
            message=message,
            custom=custom)

    def sendChangeEvent(self, model, model_pk, name="group.change", custom=None):
        if not custom:
            custom = {}
        custom["group_id"] = self.id
        RemoteEvents.sendToGroup(
            self,
            name,
            model=model,
            model_id=model_pk,
            custom=custom)

    def getStats(self):
        return {
            "members": self.memberships.count(),
            "active": self.memberships.filter(state__gte=0).count(),
            "pending_invites": self.memberships.filter(state__in=[-10,-9]).count()
        }

    def logEvent(self, kind, component=None, component_id=None, note=None):
        GroupFeed = RestModel.getModel("account", "GroupFeed")
        member = None
        request = self.getActiveRequest()
        if request:
            member = request.member
        return GroupFeed.log(member, self, kind, component, component_id, note)

    def __str__(self):
        return F"{self.name}:{self.id}"

    @classmethod
    def canSubscribeTo(cls, credentials, msg):
        # this is called by the ws4redis framework when a websocket is requesting a subscription
        # credentials are the authentication details for the websocket
        # the response is expected to be a list of primary keys these credentials have access to
        # or the single pk if msg.pk is not none if the creds have access to that key
        if credentials.kind == "member":
            if msg.pk is not None:
                if credentials.instance.hasPermission("view_all_groups") or credentials.instance.isMemberOf(msg.pk):
                    return [msg.pk]
                return None
            return credentials.instance.getGroupIDs()
        return None

    @classmethod
    def canPublishTo(cls, credentials, msg):
        # this is called by the ws4redis framework when a websocket wants to publish to a channel
        # credentials are the authentication details for the websocket
        # this should return true or false
        if credentials.kind == "member":
            if msg.pk is not None:
                return credentials.instance.isMemberOf(msg.pk)
        return False


class GroupMetaData(MetaDataBase):
    parent = models.ForeignKey(Group, related_name="properties", on_delete=models.CASCADE)
