from django.db import models
from datetime import datetime, timedelta
from rest import datem as date_util
from rest import models as rm
from rest import settings
from objict import objict

"""
This is useful for when creating daily metrics that have an end of day that is not midnight!
"""

DEFAULT_TIMEZONE = settings.get("METRICS_OFFSET_TIMEZONE", "US/Pacific")


def generate_uuid(slug, date_string, component=None, component_pk=None, group=None):
    uuid = slug
    if group is not None and component is not None:
        uuid = f"{slug}.g.{group.id}.{component}.{component_pk}:{date_string}"
    elif group is not None:
        uuid = f"{slug}.g.{group.id}:{date_string}"
    elif component is not None:
        uuid = f"{slug}.c.{component}.{component_pk}:{date_string}"
    else:
        uuid = f"{slug}:{date_string}"
    return uuid


def generate_date(date, tz=DEFAULT_TIMEZONE, eod_hour=0, eod_minute=0, granularity="daily"):
    if date is None:
        date = datetime.utcnow()
    pi = objict(tz=tz, hour=eod_hour, minute=eod_minute)
    end = date_util.convertToLocalTime(pi.tz, date)
    if end.hour >= pi.hour and end.minute >= pi.minute:
        end = end + timedelta(days=1)
    end = end.replace(hour=pi.hour, minute=pi.minute, second=0, microsecond=0)
    utc_end = date_util.convertToUTC(pi.tz, end)
    return utc_end, generate_date_string(utc_end, granularity)


def generate_date_string(when, granularity="daily"):
    date_string = when.strftime("%Y-%m-%d")
    return date_string


def metric(keys, slug, data, **kwargs):
    """
    keys: a list of ordered key names that will be used to keep data mappings in order
          key/value position 0 is the only "indexed" value
    slug: the unique slug to identify the data for the metrics
    data: a dict of key/value pairs that has values for all the keys
    component: this can be any string the represents unique data but is usually django model path
    componenet_pk: a unique key for the component
    group: optional group to map to
    tz: timezone
    eod: end of day
    """
    tz = kwargs.get("tz", DEFAULT_TIMEZONE)
    eod_hour = kwargs.get("eod_hour", 0)
    eod_minute = kwargs.get("eod_minute", 0)
    group = kwargs.get("group", None)
    component = kwargs.get("component", None)
    component_pk = kwargs.get("component_pk", None)
    when = kwargs.get("when", None)

    utc_end, date_string = generate_date(when, tz, eod_hour, eod_minute)
    uuid = generate_uuid(slug, date_string, component, component_pk, group)

    defaults = objict(slug=slug, end=utc_end)

    if group is not None:
        defaults.group_id = group.id
    if component is not None:
        defaults.component = component
        defaults.component_pk = component_pk
    mets, created = EODMetrics.objects.get_or_create(
        uuid=uuid, defaults=defaults)
    mets.updateMetrics(keys, data, update_keys=created)
    return mets


def metrics_component_group_all(keys, slug, data, **kwargs):
    """
    this method does the same as above but will generate all 3 metrics
     - global/all metrics
     - group metrics
     - component metrics
    """
    tz = kwargs.get("tz", DEFAULT_TIMEZONE)
    eod_hour = kwargs.get("eod_hour", 0)
    eod_minute = kwargs.get("eod_minute", 0)
    group = kwargs.get("group", None)
    component = kwargs.get("component", None)
    component_pk = kwargs.get("component_pk", None)
    metric(keys, slug, data, tz=tz, eod_hour=eod_hour, eod_minute=eod_minute)
    if group is not None:
        metric(
            keys, slug, data, group=group,
            tz=tz, eod_hour=eod_hour, eod_minute=eod_minute)
    if component is not None:
        metric(
            keys, slug, data, group=group,
            component=component, component_pk=component_pk,
            tz=tz, eod_hour=eod_hour, eod_minute=eod_minute)
    return True


def get_metric(slug, end=None, group=None, **kwargs):
    tz = kwargs.get("tz", DEFAULT_TIMEZONE)
    eod_hour = kwargs.get("eod_hour", 0)
    eod_minute = kwargs.get("eod_minute", 0)
    group = kwargs.get("group", None)
    component = kwargs.get("component", None)
    component_pk = kwargs.get("component_pk", None)

    utc_end, date_string = generate_date(end, tz, eod_hour, eod_minute)
    uuid = generate_uuid(slug, date_string, component, component_pk, group)
    
    obj = EODMetrics.objects.filter(uuid=uuid).last()
    return obj.getMetrics()


def get_metrics(slug, count=7, end=None, group=None, **kwargs):
    """
    returns data ready for Chart.js
    'periods': ['y:2012', 'y:2013', 'y:2014']
    'data': {
        key: value,
        etc...
    }
    """
    tz = kwargs.get("tz", DEFAULT_TIMEZONE)
    eod_hour = kwargs.get("eod_hour", 0)
    eod_minute = kwargs.get("eod_minute", 0)
    group = kwargs.get("group", None)
    component = kwargs.get("component", None)
    component_pk = kwargs.get("component_pk", None)

    utc_end, date_string = generate_date(end, tz, eod_hour, eod_minute)
    utc_now = utc_end - timedelta(days=count)
    periods = []
    missing = []
    data = None
    for i in range(0, count):
        utc_now = utc_now + timedelta(days=1)
        date_string = generate_date_string(utc_now)
        uuid = generate_uuid(slug, date_string, component, component_pk, group)
        periods.append(date_string)
        obj = EODMetrics.objects.filter(uuid=uuid).last()
        if obj is None:
            missing.append(0)
            continue
        obj_metrics = obj.getMetrics()
        if not data:
            data = dict()
            for key in obj_metrics.keys():
                data[key] = [*missing]
        for key, value in obj_metrics.items():
            data[key].append(value)
    return objict(periods=periods, data=data)


class EODMetrics(models.Model, rm.RestModel):
    class RestMeta:
        GRAPHS = {
            "default": {
                "recurse_into": ["generic__component"]
            }
        }

    created = models.DateTimeField(auto_now_add=True, editable=True)
    # timeframe of metrics is always a day and the ending day
    end = models.DateTimeField(db_index=True)
    # unique uuid of metric
    uuid = models.SlugField(max_length=250, unique=True)
    # the slug
    slug = models.CharField(max_length=200, db_index=True, null=True, default=None)
    # auto delete objects older then this
    expires = models.DateTimeField(db_index=True, null=True, default=None)
    # granularity: year, month, week, day, hour
    granularity = models.CharField(max_length=64, db_index=True)
    # our generic component
    component = models.CharField(max_length=255, db_index=True, null=True, default=None)
    # generic component primary key
    component_pk = models.IntegerField(null=True, default=None, db_index=True)
    # allow to group metrics by a group
    group_id = models.IntegerField(null=True, default=None, db_index=True)

    # now we create a set of k/v 
    k1 = models.SlugField(max_length=64, null=True, default=None)
    v1 = models.IntegerField(default=0, db_index=True)

    k2 = models.SlugField(max_length=64, null=True, default=None)
    v2 = models.IntegerField(default=0, db_index=True)

    k3 = models.SlugField(max_length=64, null=True, default=None)
    v3 = models.IntegerField(default=0)

    k4 = models.SlugField(max_length=64, null=True, default=None)
    v4 = models.IntegerField(default=0)

    k5 = models.SlugField(max_length=64, null=True, default=None)
    v5 = models.IntegerField(default=0)

    k6 = models.SlugField(max_length=64, null=True, default=None)
    v6 = models.IntegerField(default=0)

    k7 = models.SlugField(max_length=64, null=True, default=None)
    v7 = models.IntegerField(default=0)

    k8 = models.SlugField(max_length=64, null=True, default=None)
    v8 = models.IntegerField(default=0)

    k9 = models.SlugField(max_length=64, null=True, default=None)
    v9 = models.IntegerField(default=0)

    k10 = models.SlugField(max_length=64, null=True, default=None)
    v10 = models.IntegerField(default=0)

    k11 = models.SlugField(max_length=64, null=True, default=None)
    v11 = models.IntegerField(default=0)

    k12 = models.SlugField(max_length=64, null=True, default=None)
    v12 = models.IntegerField(default=0)

    k13 = models.SlugField(max_length=64, null=True, default=None)
    v13 = models.IntegerField(default=0)

    k14 = models.SlugField(max_length=64, null=True, default=None)
    v14 = models.IntegerField(default=0)

    def getMetrics(self):
        metrics = objict()
        for i in range(1, 15):
            key = getattr(self, f"k{i}", None)
            if key is None:
                return metrics
            metrics[key] = getattr(self, f"v{i}", 0)
        return metrics

    def updateMetrics(self, keys, data, update_keys=True):
        params = {}
        index = 0
        for key in keys:
            if isinstance(data, list):
                v = data[index]
            else:
                v = data[key]
            index += 1
            vkey = f"v{index}"
            params[vkey] = models.F(vkey) + v
            if update_keys or True:
                params[f"k{index}"] = key
        EODMetrics.objects.filter(pk=self.pk).update(**params)
