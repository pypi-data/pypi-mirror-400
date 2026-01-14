from django.db import models
from rest import models as rm
from rest import helpers as rh
from .. import geolocate


class Address(models.Model, rm.RestModel):
    class RestMeta:
        VIEW_PERMS = [
            "view_all_groups",
            "manage_groups",
            "manage_group",
            "manage_settings"]
        CREATE_PERMS = None  # allow anyone to create
        SAVE_PERMS = None  # allow anyone to edit
        GRAPHS = {
            "abstract": {
                "fields":[
                    ('line1', 'street1'),
                    ('line2', 'street2'),
                    'city',
                    'state',
                    ('postalcode', 'zip'),
                    'country',
                ]
            }
        }
    label = models.CharField(
        max_length=250, null=True, blank=True,
        default=None, db_index=True)
    member = models.ForeignKey(
        "account.User", null=True, blank=True,
        default=None, on_delete=models.SET_NULL, related_name="addresses")
    group = models.ForeignKey(
        "account.Group", null=True, blank=True,
        default=None, on_delete=models.SET_NULL, related_name="addresses")
    modified = models.DateTimeField(auto_now=True)
    line1 = models.CharField(max_length=255, blank=True, null=True, default=None)
    line2 = models.CharField(max_length=255, blank=True, null=True, default=None)
    city = models.CharField(max_length=127, blank=True, null=True, default=None)
    state = models.CharField(max_length=127, blank=True, null=True, default=None)
    county = models.CharField(max_length=127, blank=True, null=True, default=None)
    country = models.CharField(max_length=16, blank=True, null=True, default=None)
    postalcode = models.CharField(max_length=32, blank=True, null=True, default=None)
    postalcode_suffix = models.CharField(max_length=32, blank=True, null=True, default=None)
    lat = models.FloatField(default=0.0, blank=True)
    lng = models.FloatField(default=0.0, blank=True)

    def getTimezone(self):
        if self.lat:
            return geolocate.getTimeZone(self.lat, self.lng)
        return None

    def lookup(self):
        res = geolocate.search("{}, {}, {}".format(self.line1, self.city, self.state))
        if isinstance(res, list) and len(res):
            return res[0]
        return None

    def refresh(self):
        try:
            addr = self.lookup()
            if addr:
                if addr.county:
                    self.county = addr.county
                self.country = addr.country
                if addr.lat:
                    self.lat = addr.lat
                    self.lng = addr.lng
                if not self.postalcode and addr.postal_code:
                    self.postalcode = addr.postal_code
                if addr.postal_code_suffix:
                    self.postalcode_suffix = addr.postal_code_suffix
                super(Address, self).save()
        except Exception:
            rh.log_exception("address.refresh")

    def save(self, *args, **kwargs):
        if not self.lat:
            self.refresh()
        super(Address, self).save(*args, **kwargs)
