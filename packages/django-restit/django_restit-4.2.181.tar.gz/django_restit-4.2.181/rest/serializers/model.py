import datetime
import time
import math
from decimal import Decimal
from django.db import models
from itertools import chain
from rest import helpers
from objict import objict
__MY_CACHE__ = objict()
# from . import profiler


def serialize(instance, graph):
    if isinstance(graph, str):
        graph = instance.getGraph(graph)
    return to_dict_from_graph(instance, graph)


def to_dict_from_graph(instance, graph):
    fields = graph.get("fields", [])
    extra = graph.get("extra", [])
    exclude = graph.get("exclude", [])
    recurse_into = graph.get("recurse_into", [])
    return to_dict(instance, fields=fields, extra=extra, exclude=exclude, recurse_into=recurse_into)


def get_from_cache(cache, instance):
    if cache is not None and isinstance(instance, models.Model) and hasattr(instance, "get_class_name"):
        cn = instance.get_class_name()
        key = f"{cn}.{instance.pk}"
        if key in cache:
            return cache[key]
    return None


def add_to_cache(cache, instance, data):
    if cache is not None and isinstance(instance, models.Model) and hasattr(instance, "get_class_name"):
        cn = instance.get_class_name()
        key = f"{cn}.{instance.pk}"
        if key not in cache:
            cache[key] = data


# @profiler.timeit
def to_dict(instance, fields=None, extra=[], exclude=[], recurse_into=[], cache=None):
    cached_item = get_from_cache(cache, instance)
    if cached_item:
        return cached_item
    # this is an attempt to work around the graphs at different depths not matching
    sub_cache = cache.get("sub_cache", None) if cache is not None else None
    if cache is not None and sub_cache is None:
        cache["sub_cache"] = dict()
        sub_cache = cache.get("sub_cache", None)

    fields = get_fields(instance) if not fields else fields
    data = {}
    recursed = set()
    combined_fields = list(chain(fields, extra, recurse_into))
    for f in combined_fields:
        fin, fout = (f[0], f[1]) if isinstance(f, (list, tuple)) else (f, f)
        if fin in exclude:
            continue

        split_fin = fin.split('.')
        if len(split_fin) > 1:
            top = split_fin[0]
            if top in recursed:
                continue
            recursed.add(top)
            fin = fout = top
        if fin.startswith("generic__") and hasattr(instance, "restGetGenericRelation"):
            fin = fin.split("__")[1]
            obj = get_generic_value(instance, fin, fout)
            if obj is not None:
                data[fin] = obj
                id_key = f"{fin}_id"
                if id_key in data:
                    del data[id_key]
            continue
        value = get_field_value(instance, fin)
        if isinstance(value, models.Model):
            if fin not in recursed:
                recursed.add(fin)
            if cache is not None:
                cached_item = get_from_cache(cache, value)
                if cached_item:
                    data[fout] = cached_item
                    continue
            sfields = get_model_fields(fin, combined_fields)
            if sfields:
                data[fout] = to_dict(value, sfields, cache=sub_cache)
            elif hasattr(value, "pk"):
                data[fout] = value.pk
                # FIXME we should use _id when not showing full model
                # data[f"{fout}_id"] = value.pk
            continue
        if isinstance(value, models.Manager):
            if fin not in recursed:
                recursed.add(fin)
            sfields = get_model_fields(fin, combined_fields)
            if __MY_CACHE__.cs is None:
                __MY_CACHE__.cs = helpers.importModule("rest.serializers.collection")
            sort = None
            qset = value.all()
            if hasattr(qset.model, "RestMeta") and hasattr(qset.model.RestMeta, "DEFAULT_SORT"):
                sort = qset.model.RestMeta.DEFAULT_SORT
            data[fout] = __MY_CACHE__.cs.to_list(qset, sort=sort, fields=sfields)["data"]
            continue

        if isinstance(value, dict) and len(split_fin) > 1:
            # let us do a complete reset here to get back to basics
            recursed.remove(fin)
            # now lets try and get the sub key
            top = split_fin.pop(0)
            value = helpers.getValueForKeys(value, split_fin)
            fin, fout = (f[0], f[1]) if isinstance(f, (list, tuple)) else (f, f)
            if "." in fout:
                keys = fout.split('.')
                tmp_data = data
                for k in keys[:-1]:
                    if k not in tmp_data:
                        tmp_data[k] = dict()
                        tmp_data = data[k]
                tmp_data[keys[-1]] = value
            else:
                data[fout] = value
            continue
        try:
            if callable(value):
                data[fout] = serialize_value(value())
            else:
                data[fout] = serialize_value(value)
        except Exception as err:
            data[fout] = str(err)
            helpers.log_exception(fout)
    if cache is not None:
        add_to_cache(cache, instance, data)
    return data


def serialize_value(value):
    if isinstance(value, (str, int, float)):
        return value
    if isinstance(value, (tuple, list)):
        value = [serialize_value(v) for v in value]
    elif isinstance(value, dict):
        value = {key: serialize_value(val) for key, val in value.items()}
    elif isinstance(value, datetime.datetime):
        # return int(time.mktime(value.timetuple()))
        value = value.timestamp()
    elif isinstance(value, datetime.date):
        value = value.strftime("%Y/%m/%d")
    elif isinstance(value, float) and math.isnan(value):
        value = 0.0
    elif isinstance(value, Decimal):
        value = float(value) if not value.is_nan() else 0.0
    return value


def get_generic_value(instance, key, graph="generic"):
    obj = None
    try:
        obj = instance.restGetGenericRelation(key)
    except Exception as err:
        print(err)
        return None
    if obj is None:
        return None
    if key == graph:
        graph = "generic"
    data = to_dict_from_graph(obj, obj.getGraph(graph))
    data["model"] = getattr(instance, key)
    return data


def get_field_value(instance, key):
    if isinstance(instance, dict):
        return instance.get(key, None)
    return getattr(instance, key) if hasattr(instance, key) else None


def get_model_fields(name, fields):
    skey = f"{name}."
    slen = len(skey)
    output = []
    for f in fields:
        if isinstance(f, (list, tuple)):
            if (f[0].startswith(skey)):
                output.append((f[0][slen:], f[1]))
        elif f.startswith(skey):
            output.append(f[slen:])
    return output
    # return [(f[0][f[0].find(".")+1:], f[1]) if isinstance(f, (list, tuple)) else f[f.find(".")+1:] for f in fields if f[0].startswith(skey)]


def get_fields(qset, model=None):
    fields = None
    if isinstance(qset, dict):
        return list(qset.keys())
    elif hasattr(qset, '_meta'):
        fields = qset._meta.fields
    elif hasattr(qset, 'model'):
        fields = qset.model._meta.fields
    elif hasattr(qset, 'keys'):
        return list(qset.keys())
    elif model and hasattr(model, '_meta'):
        fields = model._meta.fields
    return [f.name for f in fields] if fields else None


def expand_fields(fields):
    output = dict()
    for key in fields:
        if "." in key:
            fields = key.split('.')
            skey = fields.pop(0)
            if output.get(skey, None) is None:
                output[skey] = []
            output[skey].append(".".join(fields))
        elif key not in output:
            output[key] = None
    expanded = objict()
    for key, value in output.items():
        if value is not None:
            expanded[key] = expand_fields(value)
        else:
            expanded[key] = None
    return expanded


def get_foreign_fields(model):
    return [field.name for field in model._meta.fields if field.get_internal_type() == "ForeignKey"]


def get_select_related_fields(model, fields):
    if isinstance(fields, list):
        fields = expand_fields(fields)
    fk_fields = get_foreign_fields(model)

    related_fields = []
    for key, value in fields.items():
        if value is not None and key in fk_fields:
            related_fields.append(key)
            fmodel = model.get_fk_model(key)
            for related in get_select_related_fields(fmodel, value):
                related_fields.append(f"{key}__{related}")
    return related_fields            
