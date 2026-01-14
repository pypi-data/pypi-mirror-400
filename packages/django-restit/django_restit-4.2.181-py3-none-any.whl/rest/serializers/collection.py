from . import model as ms
from django.db.models.query import QuerySet
from django.db.models import Count, F, Q
from rest import settings
from datetime import datetime, timedelta
# from . import profiler
from . import csv


def serialize(qset, graph, sort=None, size=25, start=0, format="json"):
    if isinstance(graph, str):
        model = getattr(qset, "model", None)
        if model:
            graph = model.getGraph(graph)
    if format == "json":
        return to_list_from_graph(qset, graph, sort, size, start)
    return to_format(qset, format, size=size).data


def to_format(qset, format, size=10000):
    model = getattr(qset, "model", None)
    fields = model.getRestFormatFields(format)
    if format == "csv":
        return csv.generateCSV(qset, fields, f"serialize.{format}")
    raise Exception("invalid format")


def to_list_from_graph(qset, graph, sort=None, size=25, start=0):
    fields = graph.get("fields", [])
    extra = graph.get("extra", [])
    exclude = graph.get("exclude", [])
    recurse_into = graph.get("recurse_into", [])
    return to_list(qset, sort, size, fields=fields, extra=extra, exclude=exclude, recurse_into=recurse_into)


def sort_nulls_last(qset, sort_args, nulls_last_fields):
    if len(sort_args) == 1 and isinstance(nulls_last_fields, list):
        arg = sort_args[0]
        if arg.startswith("-"):
            arg = arg[1:]
        if arg not in nulls_last_fields:
            return qset.order_by(*sort_args)
    new_args = []
    for arg in sort_args:
        if arg.startswith("-"):
            new_args.append(F(arg[1:]).desc(nulls_last=True))
        else:
            new_args.append(F(arg).asc(nulls_last=True))
    return qset.order_by(*new_args)


def sort_list(qset, sort):
    qset, sort_args = get_sort_args(qset, sort)
    nulls_last = False
    if hasattr(qset, "model") and hasattr(qset.model, "RestMeta"):
        nulls_last = getattr(qset.model.RestMeta, "NULLS_LAST", False)
    try:
        if nulls_last:
            qset = sort_nulls_last(qset, sort_args, nulls_last)
        else:
            qset = qset.order_by(*sort_args)
    except Exception as err:
        return qset, str(err)
    return qset, sort_args


def to_list(qset, sort=None, size=25, start=0, fields=[], extra=[], exclude=[], recurse_into=[], cache=None):
    if cache is None and isinstance(qset, QuerySet):
        cache = dict()
    output = {"size": size, "start": start}
    if sort and isinstance(qset, QuerySet):
        qset, sort_args = sort_list(qset, sort)
        output["sort"] = sort_args

    qset = qset[start:start+size]
    if not fields:
        fields = ms.get_fields(qset)
    if settings.REST_SELECT_RELATED:
        # this should improve speed greatly for lookups
        foreign_fields = ms.get_select_related_fields(qset.model, fields)
        if foreign_fields:
            qset = qset.select_related(*foreign_fields)
    data = []
    for obj in qset:
        data.append(ms.to_dict(obj, fields, extra, exclude, recurse_into, cache=cache))
    output["count"] = len(data)
    output["data"] = data
    return output


def convert_date_sort_to_dt(arg):
    v = int(arg[:-1])
    if arg.endswith("d"):
        return datetime.now() - timedelta(days=v)
    if arg.endswith("h"):
        return datetime.now() - timedelta(hours=v)
    if arg.endswith("m"):
        return datetime.now() - timedelta(minutes=v)
    return datetime.now()


def get_sort_args(qset, sort):
    if not isinstance(sort, str) or "metadata" in sort:
        return qset, None
    sort_args = []
    for s in sort.split(","):
        if s.endswith("_display"):
            # fix for django _display kinds being sorted
            s = s[:s.find("_display")]
        s = s.replace('.', '__')
        if "__count" in s:
            fields = s.split("__")
            k = fields[0]
            j = fields[1]
            s = "fk_count"
            if k.startswith("-"):
                k = k[1:]
                s = "-fk_count"

            if len(fields) > 2 and hasattr(qset.model, "RestMeta"):
                # this is a daterange field, 5m minutes, 2h hours, 40d days
                # the daterange field is the DATE_RANGE_FIELD
                dr_field = getattr(qset.model.RestMeta, "DATE_RANGE_FIELD", "created")
                dr = fields[2]
                q = {}
                q[f"{k}__{dr_field}__gte"] = convert_date_sort_to_dt(dr)
                qfilter = Q(**q)
                qset = qset.annotate(fk_count=Count(k, filter=qfilter)).distinct()
            else:
                qset = qset.annotate(fk_count=Count(k)).distinct()
        sort_args.append(s)
    return qset, sort_args
