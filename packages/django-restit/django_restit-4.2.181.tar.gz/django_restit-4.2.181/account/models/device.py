
from django.db import models
from rest import models as rm
from rest import fields as rf
from rest import settings
from objict import objict
from datetime import datetime

from rest import helpers as rh

CM_BACKENDS = objict()
DEVICE_USE_BUID = settings.get("DEVICE_USE_BUID", False)


class MemberDevice(models.Model, rm.RestModel, rm.MetaDataModel):
    """
    MemberDevice Model tracks personal devices associated with a user.
    This can include mobile and desktop devices.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    member = models.ForeignKey("account.Member", related_name="devices", on_delete=models.CASCADE)

    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    uuid = models.CharField(db_index=True, max_length=128, blank=True, null=True, default=None)
    buid = models.CharField(db_index=True, max_length=128, blank=True, null=True, default=None)

    cm_provider = models.CharField(db_index=True, max_length=64, default="fcm")
    cm_token = models.CharField(max_length=250, default=None, null=True)

    kind = models.CharField(db_index=True, max_length=64, default="unknown")
    ip = models.CharField(max_length=64, default=None, null=True)
    state = models.IntegerField(db_index=True, default=1)

    class RestMeta:
        GRAPHS = {
            "default": {
                "extra": ["metadata"],
            }
        }

    def sendData(self, message, **kwargs):
        messenger = getCloudMessenger(self.cm_provider)
        if messenger:
            resp = messenger.sendToDevice(self, message)
            return resp
        return objict(status_code=404, reason=self.cm_provider)

    def sendNotification(self, title, body):
        messenger = getCloudMessenger(self.cm_provider)
        if messenger:
            resp = messenger.sendNotification(self.cm_token, title, body)
            return resp
        return objict(status_code=404, reason=self.cm_provider)

    def notify(self, title, body):
        return self.sendNotification(title, body)

    def touch(self, ip=None):
        if ip is not None:
            self.ip = ip
        self.modified = datetime.now()
        self.save()

    @classmethod
    def sendMessageTo(cls, message, devices, **kwargs):
        pass

    @classmethod
    def register(cls, request, member, device_id):
        cm_token = request.DATA.get("cm_token")
        default_provider = "ws"
        if cm_token is not None:
            default_provider = "fcm"
        cm_provider = request.DATA.get("cm_provider", default=default_provider)
        buid = request.DATA.get("__buid__", None)
        md = MemberDevice.objects.filter(uuid=device_id, member=member).last()
        if md is not None:
            if md.cm_token != cm_token:
                md.cm_token = cm_token
            if buid and md.buid != buid:
                md.buid = buid
            if cm_provider is not None:
                md.cm_provider = cm_provider
            if md.state != 1:
                md.state = 1
            md.touch(request.ip)
            metadata = request.DATA.get("device_metadata", None)
            rh.debug("md.metadata", metadata)
            if metadata is not None:
                md.setProperty("device", metadata)
            return md
        md = MemberDevice(
            uuid=device_id, buid=buid,
            member=member, cm_token=cm_token,
            cm_provider=cm_provider)
        md.ip = request.ip
        md.name = F"{member.first_name} {request.auth_session.device}"
        md.kind = request.auth_session.os.lower()
        if md.kind.startswith("mac"):
            md.kind = "mac"
        md.save()
        md.setProperty("user_agent", request.META.get('HTTP_USER_AGENT', ''))
        metadata = request.DATA.get("device_metadata", None)
        if metadata is not None:
            md.setProperty("device", metadata)
        return md

    @classmethod
    def unregister(cls, member, device_id):
        md = MemberDevice.objects.filter(uuid=device_id, member=member, state=1).last()
        if md is None:
            return False
        md.cm_token = None
        md.state = -1
        md.save()
        return True


class MemberDeviceMetaData(rm.MetaDataBase):
    parent = models.ForeignKey(MemberDevice, related_name="properties", on_delete=models.CASCADE)


class CloudCredentials(models.Model, rm.RestModel, rm.MetaDataModel):
    """
    CloudCredentials is a global setting for a group to store this groups cloud credentials.
    """
    class RestMeta:
        VIEW_PERMS = ["view_cm", "manage_cm"]
        EDIT_PERMS = ["manage_cm"]
        GRAPHS = {
            "default": {
                "extra": ["metadata"],
                "graphs": {
                    "group": "basic"
                }
            }
        }

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(
        "account.Group", null=True, default=None,
        related_name="cloud_credentials", on_delete=models.CASCADE)

    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    uuid = models.CharField(db_index=True, max_length=64, blank=True, null=True, default=None)
    state = models.IntegerField(db_index=True, default=1)

    # specify the cloud provider class "account.fcm.v1.FirebaseNotifier"
    # provider_class = models.CharField(max_length=255, null=True, default=None)

    credentials = rf.JSONField()

    _notifier = None

    @property
    def notifier(self):
        if self._notifier is None:
            from account import fcm
            self._notifier = fcm.v1.FirebaseNotifier(self.credentials) 
        return self._notifier

    def sendToDevice(self, device, message):
        return self.notifier.send(device.cm_token, None, None, message)

    def sendNotification(self, token, title, body):
        return self.notifier.send(token, title, body)


class CloudCredentialsMetaData(rm.MetaDataBase):
    parent = models.ForeignKey(CloudCredentials, related_name="properties", on_delete=models.CASCADE)


def getCloudMessenger(name):
    creds = CloudCredentials.objects.filter(uuid=name).last()
    if creds is not None:
        return creds
    return None
