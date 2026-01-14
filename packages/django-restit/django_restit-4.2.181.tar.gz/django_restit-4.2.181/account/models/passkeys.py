
from django.db import models
from rest import models as rm
from rest import fields as rf
from rest import settings
from objict import objict
from datetime import datetime


class UserPassKey(models.Model, rm.RestModel):
    """
    A “Passkey” is a modern, secure authentication method designed to replace
    traditional passwords with more robust and user-friendly alternatives.
    It leverages cryptographic techniques and is based on standards like
    WebAuthn and FIDO2, aiming to improve both security and convenience.
    """
    class RestMeta:
        VIEW_PERMS = ["manage_users", "owner"]
        CAN_DELETE = True
        VIEW_PERMS_MEMBER_FIELD = "member"
        GRAPHS = {
            "default": {
                "fields": [
                    "id", "created", "modified", "last_used",
                    "uuid", "rp_id", "is_enabled", 
                    "name", "platform", "info"
                ],
            }
        }
        
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    member = models.ForeignKey("account.Member", related_name="passkeys", on_delete=models.CASCADE)

    uuid = models.CharField(max_length=255, unique=True)
    rp_id = models.CharField(max_length=255, null=False, db_index=True)
    is_enabled = models.BooleanField(default=True, db_index=True)

    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=255, default='')
    last_used = models.DateTimeField(null=True, default=None)
    token = models.CharField(max_length=255, null=False)

    info = rf.JSONField()

    def touch(self):
        self.last_used = datetime.now()
        self.save()



