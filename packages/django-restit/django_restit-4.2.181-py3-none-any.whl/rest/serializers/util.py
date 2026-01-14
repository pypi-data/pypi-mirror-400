import inspect
import json
import time
import datetime
import math
from decimal import Decimal


def rest_serialize(data):
    if isinstance(data, datetime.datetime):
        try:
            return time.mktime(data.timetuple())
        except Exception:
            print(("invalid date: {0}".format(data)))
        return 0.0
    elif isinstance(data, datetime.date):
        return data.strftime("%Y/%m/%d")
    elif isinstance(data, dict):
        data = data.copy()
        for k in list(data.keys()):
            data[k] = rest_serialize(data[k])
    elif isinstance(data, list) or isinstance(data, tuple):
        newdata = []
        for v in data:
            newdata.append(rest_serialize(v))
        data = newdata
    elif isinstance(data, float):
        if math.isnan(data):
            return 0.0
    elif isinstance(data, Decimal):
        if data.is_nan():
            return 0.0
        return float(data)
    return data


def requestInPaths(request, paths):
    for ep in paths:
        if request.path.startswith(ep):
            return True
    return False


def _getFields(qset=None, model=None):
    """
    returns a list of fields for specified QuerySet or Model
    """
    if hasattr(qset, '_meta') and getattr(qset, '_meta') != None:
        fields = qset._meta.fields
    elif hasattr(qset, 'model') and getattr(qset, 'model') != None:
        fields = qset.model._meta.fields
    elif hasattr(qset, 'keys'):
        return list(qset.keys())
    elif hasattr(model, '_meta') and getattr(model, '_meta') != None:
        fields = model._meta.fields
    else:
        return None
    if fields:
        return list(f.name for f in fields)
    return None


def _filter_recurse(remove, lst):
    if isinstance(lst, dict):
        ret = {}
    else:
        ret = []
    for item in lst:
        if isinstance(lst, dict):
            if item[:len(remove)+1] == remove + ".":
                ret[item[len(remove)+1:]] = lst[item]
        elif type(item) in (list,tuple) and type(item[0]) in (str, str):
            p = item[0]
            if p[:len(remove)+1] == remove + ".":
                ret.append((p[len(remove)+1:], item[1]))
        elif isinstance(item, str):
            if item[:len(remove)+1] == remove + ".":
                ret.append(item[len(remove)+1:])

    return ret


def __call_func(func, *args, **kwargs):
    if not kwargs:
        return func(*args)
    if hasattr(inspect, "getargspec"):
        # removed in python3.11 (but much faster)
        take = inspect.getargspec(func)[0]
    else:
        take = list(inspect.signature(func).parameters.keys())
    give = {}
    for arg in kwargs:
        if arg in take:
            give[arg] = kwargs[arg]
    return func(*args, **give)