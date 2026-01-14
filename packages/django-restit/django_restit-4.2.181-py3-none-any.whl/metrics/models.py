from django.db import models
from django.db.models import Sum, Max, Count, Q
from django.db.models.functions import Trunc
from rest import helpers as rh
from rest import models as rm
from rest import settings
from datetime import datetime, timedelta
from rest import datem as date_util
from objict import objict
from . import utils
from .eod import EODMetrics

# THIS IS IN DAYS
METRICS_EXPIRE_HOURLY = settings.get("METRICS_EXPIRE_HOURLY", 90)
METRICS_EXPIRE_DAILY = settings.get("METRICS_EXPIRE_DAILY", 360)
METRICS_EXPIRE_WEEKLY = settings.get("METRICS_EXPIRE_WEEKLY", 360)

def metric(
    slug, keys, data, min_granularity="hourly",
    group=None, date=None, timezone=None, slug_append=None,
    max_granularity=None
):
    # keys is a ordered list of keys to map to k1,k2,etc
    # data is a dict of key/values
    uuid_key = generate_uuid(slug, group, slug_append)
    granularities = utils.granularities(min_granularity, max_granularity)
    date = normalize_date(date, timezone, group)

    uuids = utils.build_keys(
        uuid_key, date,
        min_granularity=min_granularity,
        max_granularity=max_granularity)

    for granularity, key in zip(granularities, uuids):
        # DO not change slug to uuid_key so we can filter by group using group field
        expires = None
        if granularity == "hourly":
            expires = datetime.now() + timedelta(days=METRICS_EXPIRE_HOURLY)
        elif granularity == "daily":
            expires = datetime.now() + timedelta(days=METRICS_EXPIRE_DAILY)
        elif granularity == "weekly":
            expires = datetime.now() + timedelta(days=METRICS_EXPIRE_WEEKLY)
        elif granularity in ["minutes", "seconds"]:
            expires = datetime.now() + timedelta(days=7)
        m, created = Metrics.objects.get_or_create(
            uuid=key,
            defaults=dict(
                granularity=granularity, slug=slug, expires=expires,
                group=group, start=utils.date_for_granulatiry(date, granularity)))
        m.updateMetrics(keys, data, created)


def gauge(slug, keys, data, granularity="daily", group=None, date=None,
          timezone=None, slug_append=None, max_granularity=None):
    # guage does not accumulate but just stores the data like a cache
    # if calledf on the same time period it will just update the current numbers
    if max_granularity is None:
        max_granularity = granularity
    uuid_key = generate_uuid(slug, group, slug_append)
    granularities = utils.granularities(granularity, max_granularity)
    date = normalize_date(date, timezone, group)
    uuids = utils.build_keys(
        uuid_key, date,
        min_granularity=granularity,
        max_granularity=max_granularity)

    for gran, key in zip(granularities, uuids):
        # DO not change slug to uuid_key so we can filter by group using group field
        expires = None
        if gran == "hourly":
            expires = datetime.now() + timedelta(days=METRICS_EXPIRE_HOURLY)
        elif gran == "daily":
            expires = datetime.now() + timedelta(days=METRICS_EXPIRE_DAILY)
        m, created = Metrics.objects.get_or_create(
            uuid=key,
            defaults=dict(
                granularity=gran, slug=slug, expires=expires,
                group=group, start=utils.date_for_granulatiry(date, gran)))
        m.setMetrics(keys, data, created)


def normalize_date(date=None, timezone=None, group=None):
    if date is None:
        date = utils.datetime.utcnow()
    if timezone is not None:
        date = date_util.convertToLocalTime(timezone, date)
    elif group:
        date = group.getLocalTime(date)
    elif settings.METRICS_TIMEZONE:
        date = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, date)
    return date


def get_qset(slug, granularity, start=None, end=None,
             group=-1, starts_with=False, ends_with=None):
    if start is None:
        start = utils.datetime.utcnow()
    if group is not None and group != -1:
        start = group.getLocalTime(start)
    elif settings.METRICS_TIMEZONE:
        start = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, start)

    start = utils.date_for_granulatiry(start, granularity)
    if end is None:
        if granularity == "hourly":
            end = start + timedelta(minutes=5)
        else:
            end = start + timedelta(hours=12)
    elif group != -1 and end:
        end = group.getLocalTime(end)
    elif settings.METRICS_TIMEZONE:
        end = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, end)
    q = {
        "granularity": granularity,
        "start__gte": start,
        "start__lte": end
    }
    if group != -1:
        q["group"] = group
    if starts_with:
        q["slug__startswith"] = slug
    else:
        q["slug"] = slug
    if ends_with:
        q["slug__endswith"] = ends_with
    return Metrics.objects.filter(**q)


def get_totals(slug, keys, granularity, start=None, end=None, group=None):
    if start is None:
        start = utils.datetime.utcnow()
    if group:
        start = group.getLocalTime(start)
    elif settings.METRICS_TIMEZONE:
        start = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, start)

    start = utils.date_for_granulatiry(start, granularity)
    if end is None:
        end = start + timedelta(minutes=5)
    elif group and end:
        end = group.getLocalTime(end)
    elif settings.METRICS_TIMEZONE:
        end = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, end)

    qset = Metrics.objects.filter(
        slug=slug, granularity=granularity,
        group=group, start__gte=start, start__lte=end)
    vkeys = [f"v{i}" for i in range(1, len(keys)+1)]
    sums = rh.getSum(qset, *vkeys)
    out = objict()
    i = 1
    for k in keys:
        out[k] = sums[f"v{i}"]
        i += 1
    return objict(slug=slug, granularity=granularity, start=start, end=end, values=out)


def get_metric(slug, granularity, start, group=None):
    if start is None:
        start = utils.datetime.utcnow()
    if group:
        start = group.getLocalTime(start)
    elif settings.METRICS_TIMEZONE:
        start = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, start)

    start = utils.date_for_granulatiry(start, granularity)
    qset = Metrics.objects.filter(
        slug=slug, granularity=granularity, start__gte=start, start__lte=start, group=group)
    m = qset.last()
    if m is None:
        return objict()
    return m.getMetrics()


def get_metrics(slug, granularity, start, end=None, group=None, samples=None):
    """
    returns data ready for Chart.js
    'periods': ['y:2012', 'y:2013', 'y:2014']
    'data': [
      {
        'slug': 'bar',
        'values': [1, 2, 3]
      },
      {
        'slug': 'foo',
        'values': [4, 5, 6]
      },
    ]
    """
    # convert to local time of group or metrics
    has_start = start is not None
    start = utils.getLocalDate(start, group)
    end = utils.getLocalDate(end, group)
    # convert to granularit start and end
    if not has_start:
        # this will find a new start based on the granularity and sample size
        start = utils.start_by_granularity(granularity, start, samples=samples)
    # set the correct end for this granularity
    end = utils.date_for_granulatiry(end, granularity)
    qset = Metrics.objects.filter(
        slug=slug, granularity=granularity, start__gte=start, start__lte=end, group=group)
    # now we want to get the keys from the most recent object (latest keys if changed)
    keys = None
    obj = qset.last()
    if obj is None:
        return objict(periods=[], data={})
    values = obj.getMetrics()
    keys = values.keys()
    period_values = []
    for obj in qset.order_by("uuid"):
        values = obj.getMetrics()
        pvals = objict(uuid=obj.uuid, period=utils.slug_to_label(obj.uuid), values=values)
        period_values.append(pvals)
    periods = get_chart_periods(slug, granularity, start, end)
    # now we assume that our raw metrics are sorted correctly
    data = dict()
    if keys is None:
        return objict(periods=periods, data=data)
    for k in keys:
        data[k] = []
    # this logic is not perfect
    # it will find the first match first the last match
    for period in periods:
        result = next((d for d in period_values if d.get("period") == period), None)
        if result is None:
            for k in keys:
                data[k].append(0)
            continue
        for k in keys:
            data[k].append(result["values"].get(k, 0))
        period_values.remove(result)
    return objict(periods=periods, data=data)


def get_chart_periods(slug, granularity, start, end=None, group=None):
    if end is None:
        start, end = get_adjusted_date_range(granularity, start, end, group=group)
    periods = []
    for date in utils.date_range(granularity, start, end):
        period = utils.slug_to_label(utils.build_keys(slug, date, granularity)[0])
        periods.append(period)
    if granularity != "weekly":
        periods.reverse()
    return periods


def get_adjusted_date_range(granularity, start, end, group=None, samples=None):
    if start is None:
        if group is not None:
            start = group.getLocalTime(start)
        else:
            start = utils.getLocalDate(None)
        end = start
        start = utils.start_by_granularity(granularity, start, samples=samples)
    elif group:
        start = group.getLocalTime(start)
    elif settings.METRICS_TIMEZONE:
        start = date_util.convertToLocalTime(settings.METRICS_TIMEZONE, start)
    if end is None:
        end = utils.datetime.utcnow()
    end = utils.date_for_granulatiry(end, granularity)
    return start, end


def get_category_metrics(category, since=None, granularity="daily"):
    """Create/Increment a metric."""
    # r = get_r()
    # slugs = [utils.to_string(s) for s in list(r.category_slugs(category))]
    # print(slugs)
    # return r.get_metric_history_chart_data(slugs, since, granularity)
    return None


def generate_uuid(slug, group, slug_append=None):
    if group is not None and slug_append is not None:
        return f"{slug}.{slug_append}.{group.pk}"
    elif group is not None:
        return f"{slug}.{group.pk}"
    return slug


class Metrics(models.Model, rm.RestModel):
    class RestMeta:
        QUERY_FIELDS = ["group__kind", "all_fields"]
        ESTIMATE_COUNTS = True
        GRAPHS = {
            "detailed": {
                "fields": [
                    "id", "created", "start",
                    "granularity", "uuid",
                    "slug"
                ],
                "extra": [("getMetrics", "metrics")],
                "graphs": {
                    "group": "basic"
                }
            }
        }

    created = models.DateTimeField(auto_now_add=True, editable=True)
    # timeframe of metrics
    start = models.DateTimeField(db_index=True)
    # auto delete objects older then this
    expires = models.DateTimeField(db_index=True, null=True, default=None)
    # granularity: year, month, week, day, hour
    granularity = models.CharField(max_length=64, db_index=True)
    # unique uuid of metric
    uuid = models.SlugField(max_length=124, unique=True)
    # kind/slug of metric
    slug = models.SlugField(max_length=124, db_index=True)
    # allow to group metrics by a group
    group = models.ForeignKey("account.Group", related_name="+", on_delete=models.CASCADE, null=True, default=None)

    # now we create a set of k/v
    k1 = models.SlugField(max_length=64, null=True, default=None)
    v1 = models.BigIntegerField(default=0)

    k2 = models.SlugField(max_length=64, null=True, default=None)
    v2 = models.BigIntegerField(default=0)

    k3 = models.SlugField(max_length=64, null=True, default=None)
    v3 = models.BigIntegerField(default=0)

    k4 = models.SlugField(max_length=64, null=True, default=None)
    v4 = models.BigIntegerField(default=0)

    k5 = models.SlugField(max_length=64, null=True, default=None)
    v5 = models.BigIntegerField(default=0)

    k6 = models.SlugField(max_length=64, null=True, default=None)
    v6 = models.BigIntegerField(default=0)

    k7 = models.SlugField(max_length=64, null=True, default=None)
    v7 = models.BigIntegerField(default=0)

    k8 = models.SlugField(max_length=64, null=True, default=None)
    v8 = models.BigIntegerField(default=0)

    k9 = models.SlugField(max_length=64, null=True, default=None)
    v9 = models.BigIntegerField(default=0)

    k10 = models.SlugField(max_length=64, null=True, default=None)
    v10 = models.BigIntegerField(default=0)

    k11 = models.SlugField(max_length=64, null=True, default=None)
    v11 = models.BigIntegerField(default=0)

    k12 = models.SlugField(max_length=64, null=True, default=None)
    v12 = models.BigIntegerField(default=0)

    k13 = models.SlugField(max_length=64, null=True, default=None)
    v13 = models.BigIntegerField(default=0)

    k14 = models.SlugField(max_length=64, null=True, default=None)
    v14 = models.BigIntegerField(default=0)

    def getMetrics(self):
        metrics = objict()
        for i in range(1, 15):
            key = getattr(self, f"k{i}", None)
            if key is None:
                return metrics
            metrics[key] = getattr(self, f"v{i}", 0)
        return metrics

    def setMetrics(self, keys, data, update_keys=False):
        self.updateMetrics(keys, data, update_keys, False)

    def updateMetrics(self, keys, data, update_keys=False, add_values=True):
        params = {}
        index = 0
        if not update_keys:
            # this fixes bug when adding new keys after creation
            i = len(keys)
            update_keys = getattr(self, f"k{i}", None) != keys[-1]
        for key in keys:
            if isinstance(data, list):
                v = data[index]
            else:
                v = data[key]
            index += 1
            vkey = f"v{index}"
            if add_values:
                params[vkey] = models.F(vkey) + v
            else:
                params[vkey] = v
            if update_keys:
                params[f"k{index}"] = key
        Metrics.objects.filter(pk=self.pk).update(**params)
