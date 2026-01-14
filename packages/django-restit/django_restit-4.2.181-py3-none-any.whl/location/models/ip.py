from django.db import models
from django.db.transaction import atomic
from rest import models as rm
from rest import settings
from datetime import datetime, timedelta
import time
from .. import geolocate

GEOIP_LOOKUP_BY_SUBNET = settings.get("GEOIP_LOOKUP_BY_SUBNET", True)


class GeoIP(models.Model, rm.RestModel):
    class RestMeta:
        SEARCH_FIELDS = ["ip", "isp"]
        CAN_DELETE = False

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    hostname = models.CharField(max_length=255, blank=True, null=True, default=None)
    ip = models.CharField(max_length=64, db_index=True)
    subnet = models.CharField(max_length=64, db_index=True, default=None, null=True)
    isp = models.CharField(max_length=84)

    city = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postal = models.CharField(max_length=32, blank=True, null=True)

    lat = models.FloatField(default=0.0, blank=True)
    lng = models.FloatField(default=0.0, blank=True)

    def __str__(self):
        return f"<GeoIP: {self.ip} {self.lat}:{self.lng}"

    @property
    def age(self):
        return (datetime.now() - self.modified).total_seconds()
    
    def isStale(self, days=300):
        stale = self.modified + timedelta(days=days)
        return stale < datetime.now()

    def refreshFromDB(self):
        if self.pk and self.country is None and self.age < 30.0:
            time.sleep(0.5)
            self.refresh_from_db()

    def refresh(self, using=None):
        if self.ip == "127.0.0.1":
            self.isp = "local"
            self.hostname = "localhost"
            self.subnet = "127.0.0"
            self.modified = datetime.now()
            self.save(using=using)
            return
        # save now to stop double lookups
        if not self.pk:
            self.isp = "unknown"
            self.saveNow(using)
        res = geolocate.locateByIP(self.ip)
        if res is None:
            self.modified = datetime.now()
            self.save(using=using)
            return
        self.hostname = res.hostname
        if res.isp is None:
            self.isp = "unknown"
        else:
            self.isp = res.isp[:83]
        self.city = res.city
        self.state = res.state
        self.country = res.country
        self.postal = res.postal
        try:
            self.lat = float(res.latitude)
            self.lng = float(res.longitude)
        except Exception:
            pass
        self.save(using=using)

    @atomic
    def saveNow(self, using=None):
        # force saves now
        self.save(using=using)

    @classmethod
    def get(cls, ip, force_refresh=False, stale_after=300):
        return cls.lookup(ip, force_refresh, stale_after)

    @classmethod
    def lookup(cls, ip, force_refresh=False, stale_after=300, using=None):
        if isinstance(ip, str):
            ip = ip.strip()
        if not geolocate.isIP(ip):
            ip = geolocate.dnsToIP(ip)
            if ip is None:
                return None
        subnet = ip[:ip.rfind(".")]
        gip = GeoIP.objects.filter(ip=ip).first()
        if gip is None:
            gip = GeoIP(ip=ip, subnet=subnet)
            if GEOIP_LOOKUP_BY_SUBNET:
                subgip = GeoIP.objects.filter(subnet=subnet).last()
                if subgip:
                    gip.lat = subgip.lat
                    gip.lng = subgip.lng
                    gip.city = subgip.city
                    gip.state = subgip.state
                    gip.country = subgip.country
                    gip.postal = subgip.postal
                    gip.isp = subgip.isp[:83]
                    gip.save()
                else:
                    gip.refresh(using=using)
            else:
                gip.refresh(using=using)
        else:
            if force_refresh or gip.isStale(stale_after):
                gip.refresh(using=using)
            else:
                gip.refreshFromDB()
            if gip.subnet is None:
                gip.subnet = subnet
                gip.save()
        return gip

    @staticmethod
    def removeDuplicates():
        # Find all ip_addresses that have duplicates
        # would be good to figure out how to not create duplicates
        duplicates = GeoIP.objects.values('ip')\
                                  .annotate(ip_count=models.Count('id'))\
                                  .filter(ip_count__gt=1)
        for entry in duplicates:
            # Get the first instance of MyModel for this ip_address
            first_instance = GeoIP.objects.filter(ip=entry['ip'])\
                                            .order_by('id').first()
            # Find all related models
            for rel in GeoIP._meta.related_objects:
                if isinstance(rel, models.ForeignKey):
                    related_model = rel.related_model
                    fk_field = rel.field.name
                    # Update the ForeignKey in each related model
                    related_model.objects.filter(**{f"{fk_field}__ip": entry['ip']})\
                                         .exclude(**{fk_field: first_instance})\
                                         .update(**{fk_field: first_instance})
                elif isinstance(rel, models.ManyToOneRel):
                    related_model = rel.related_model
                    fk_field = rel.field.name
                    # print(f"{rel}.{related_model}.{fk_field}")
                    related_model.objects.filter(**{f"{fk_field}__ip": entry['ip']})\
                                         .exclude(**{fk_field: first_instance})\
                                         .update(**{fk_field: first_instance})

            # Delete the duplicate MyModel instances, keeping the first one
            GeoIP.objects.filter(ip=entry['ip'])\
                         .exclude(id=first_instance.id)\
                         .delete()
