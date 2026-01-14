from django.db import models
# from django.db.models import Q
from rest import settings
import time
from objict import objict

from rest.models import RestModel, MetaDataModel, MetaDataBase, RestValidationError


DEFAULT_ROLE = settings.get("MEMBERSHIP_DEFAULT_ROLE", "guest")


class Membership(models.Model, RestModel, MetaDataModel):
    class RestMeta:
        CAN_DELETE = True
        SEARCH_FIELDS = ["role", "member__username", "member__first_name", "member__last_name", "member__email"]
        LIST_DEFAULT_FILTERS = {
            "state__gte": 0
        }
        LIST_PARENT_KINDS = []
        VIEW_PERMS = ["view_all_groups", "manage_members", "manage_group", "manage_users", "manage_groups", "owner"]
        VIEW_PERMS_MEMBER_FIELD = "member"
        SAVE_PERMS = ["manage_groups", "create_groups", "manage_users", "manage_members"]
        CREATE_PERMS = ["manage_groups", "create_groups", "manage_users", "manage_members"]
        SEARCH_TERMS = [
            ("username", "member__username"),
            ("email", "member__email"),
            ("first_name", "member__first_name"),
            ("last_name", "member__last_name"),
            ("last_activity", "member__last_activity#datetime"),
            ("created", "member__datejoined#datetime"),
            ("perms", "properties|permissions."),
            "role"]
        METADATA_FIELD_PROPERTIES = settings.MEMBERSHIP_METADATA_PROPERTIES
        GRAPHS = {
            "default": {
                "extra": ["metadata"],
                "fields": [
                    'id',
                    'created',
                    'role',
                    'status',
                    'state'
                ],
                "graphs": {
                    "member": "basic"
                },
            },
            "list": {
                "extra": ["metadata"],
                "fields": [
                    'id',
                    'created',
                    'role',
                    'status',
                    'state'
                ],
                "graphs": {
                    "member": "basic",
                    "group": "basic"
                },
            },
            "detailed": {
                "graphs": {
                    "self": "default",
                    "member": "detailed",
                }
            }
        }

    member = models.ForeignKey("account.Member", related_name="memberships", on_delete=models.CASCADE)
    group = models.ForeignKey("account.Group", related_name="memberships", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=64, blank=True, null=True, default=DEFAULT_ROLE)
    state = models.IntegerField(default=0)

    @property
    def is_enabled(self):
        return self.state >= -10

    def set_action(self, value):
        if value == "resend_invite":
            self.sendInvite(self.getActiveRequest())

    def sendInvite(self, request=None, url=None, subject=None, site_logo=None, company_name=None, msg=None):
        if request:
            powered_by = request.DATA.get("powered_by", True)
            subject = request.DATA.get("invite_subject")
            url = request.DATA.get("invite_url")
            site_logo = request.DATA.get("site_logo", settings.SITE_LOGO)
            company_name = request.DATA.get("company_name", settings.COMPANY_NAME)
            msg = request.DATA.get("invite_msg", None)
        else:
            powered_by = True
            site_logo = settings.SITE_LOGO
            company_name = settings.COMPANY_NAME
        if url is None:
            raise RestValidationError("requires url", -1)
        if "?" not in url:
            url += "?jjj=1"
        if subject is None:
            subject = F"Invitation to {self.group.name}"
        is_new = not self.member.hasLoggedIn()
        btn_label = "ACCEPT"
        if is_new and url is not None:
            btn_label = "ACCEPT"
            expires = time.time() + 172800
            self.member.generateAuthCode(expires=expires)
            auth_token = objict(username=self.member.username, auth_token=self.member.auth_code)
            url = "{}&auth_code={}".format(url, auth_token.toBase64())
        self.member.sendInvite(
            subject, self.group, url=url, 
            msg=msg, 
            POWERED_BY=powered_by,
            SITE_LOGO=site_logo,
            COMPANY_NAME=company_name,
            btn_label=btn_label)

    def set_state(self, value):
        if self.state != value:
            if value < -10:
                request = self.getActiveRequest()
                by_user = "system"
                if request:
                    by_user = request.member.username
                    request.member.auditLog(F"disabled {self.member.username} access to {self.group.name}", "membership_disabled")
                # we are disabling this member
                msg = F"{self.member.username} access to {self.group.name} disabled by {by_user}"
                self.auditLog(msg, "membership_disabled")
                self.member.auditLog(msg, "membership_disabled")
                self.group.auditLog(msg, "membership_disabled")
                self.state = value
            elif self.state < -10 and value >= -10:
                request = self.getActiveRequest()
                by_user = "system"
                if request:
                    by_user = request.member.username
                    request.member.auditLog(F"enabled {self.member.username} access to {self.group.name}", "membership_enabled")
                msg = F"{self.member.username} access to {self.group.name} enabled by {by_user}"
                self.auditLog(msg, "membership_enabled")
                self.member.auditLog(msg, "membership_enabled")
                self.group.auditLog(msg, "membership_enabled")
                self.state = value
            else:
                self.state = value
    
    def set_permissions(self, value):
        if isinstance(value, dict):
            self.setProperties(value, category="permissions")
        elif isinstance(value, list):
            for k in value:
                self.addPermission(k)

    def addPermission(self, perm):
        self.setProperty(perm, 1, "permissions")

    def removePermission(self, perm):
        self.setProperty(perm, None, "permissions")

    def clearPermissions(self):
        return self.properties.filter(category="permissions").delete()

    def getPermissions(self):
        return list(self.properties.filter(category="permissions", int_value__gt=0).values_list("key", flat=True))

    def hasPermission(self, perm):
        return self.hasPerm(perm)

    def hasPerm(self, perm):
        if not self.is_enabled:
            return False
        if isinstance(perm, list):
            for i in perm:
                if self.hasPerm(i):
                    return True
            return False
        return self.getProperty(perm, 0, "permissions", bool)

    def hasRole(self, role):
        if not self.is_enabled:
            return False
        if type(role) is list:
            return self.role in role
        return self.role == role

    # SUPPORT FOR LEGACY PERMS
    def set_perms(self, value):
        if isinstance(value, dict):
            for k, v in list(value.items()):
                if v in [1, "1", True, "true"]:
                    self.addPermission(k)
                elif v in [0, "0", False, "false"]:
                    self.removePermission(k)
        elif isinstance(value, list):
            perms = self.perms
            for k in perms:
                if k not in value:
                    self.removePermission(k)
            for k in value:
                self.addPermission(k)

    def on_rest_deleted(self, request):
        # called right before the delete
        msg = f"{self.member.username} membership deleted for {self.group.name}:{self.group.pk} by {request.member.username}"
        self.member.auditLog(msg, "membership_deleted")
        self.group.auditLog(msg, "membership_deleted")
        # request.member(msg, "deleted_membership")
        # check if we should delete children
        if request.DATA.get("delete_children", False, field_type=bool):
            groups = self.group.getAllChildren(False, True, True)
            for g in groups:
                for ms in g.memberships.filter(member=self.member):
                    msg = f"{self.member.username} membership deleted for {ms.group.name}:{ms.group.pk} by {request.member.username}"
                    ms.member.auditLog(msg, "membership_deleted")
                    ms.group.auditLog(msg, "membership_deleted")
                    # request.member(msg, "deleted_membership")
                    ms.delete()

    def on_rest_created(self, request):
        msg = f"{self.member.username} membership added for {self.group.name}:{self.group.pk} by {request.member.username}"
        self.member.auditLog(msg, "membership_added")
        self.group.auditLog(msg, "membership_added")

    def __str__(self):
        return F"{self.group}:{self.member}:{self.id}"


class MembershipMetaData(MetaDataBase):
    parent = models.ForeignKey(Membership, related_name="properties", on_delete=models.CASCADE)
