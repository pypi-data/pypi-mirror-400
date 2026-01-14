from . import models as auditlog
from . import cloudwatch

from rest import views as rv
from rest import decorators as rd
from datetime import datetime


@rd.url(r'^plog$')
@rd.url(r'^plog/(?P<plog_id>\d+)$')
@rd.perm_required('view_logs')
def plog_handler(request, plog_id=None):
    if not plog_id:
        min_pk = getattr(auditlog.settings, "PLOG_STALE_ID", 0)
        return auditlog.PersistentLog.on_rest_list(request, qset=auditlog.PersistentLog.objects.filter(pk__gte=min_pk))
    return auditlog.PersistentLog.on_rest_request(request, plog_id)


@rd.urlGET(r'^plog_old$')
@rd.perm_required('view_logs')
def plogList(request):
    auditlog.PersistentLog.on_request_handle()

    graph = request.DATA.get("graph", "default")
    qset = auditlog.PersistentLog.objects.all()
    if request.group:
        qset = qset.filter(group=request.group)

    ip = request.DATA.get("ip")
    if ip:
        qset = qset.filter(session__ip=ip)

    path = request.DATA.get("path")
    if path:
        qset = qset.filter(remote_path__icontains=path)
    
    method = request.DATA.get("method")
    if method:
        qset = qset.filter(method=method)

    action = request.DATA.get("action")
    if action:
        qset = qset.filter(action=action)
    
    component = request.DATA.get("component")
    if component:
        qset = qset.filter(component=component)
    
    pkey = request.DATA.get("pkey")
    if pkey:
        qset = qset.filter(pkey=pkey)

    username = request.DATA.get("username")
    if username:
        qset = qset.filter(user__username=username)
    
    term = request.DATA.get("term")
    if term:
        qset = qset.filter(message__icontains=term)
    
    return rv.restList(request, qset.order_by('-when'), **auditlog.PersistentLog.getGraph(graph))


@rd.url('server/logs')
@rd.perm_required('view_logs')
@rd.requires_params(["log_group", "log_streams"])
def cloudwatch_logs(request):
    log_group = request.DATA.get("log_group")
    log_streams = request.DATA.get("log_streams").split(',')
    pattern = request.DATA.get("search")
    if not pattern:
        data = dict(status=True, data=[], count=0)
        return rv.restResult(request, data)
    start = request.DATA.get("dr_start", "1d")
    end = request.DATA.get("dr_end", field_type=datetime)
    resp = cloudwatch.filter(log_group, log_streams, pattern,
                             start_time=start, end_time=end,
                             resp_format="nginx")
# else:
    #     resp = cloudwatch.get(log_group, log_streams, resp_format="nginx")
    lst = resp["events"]
    count = len(lst)
    data = dict(status=True, data=lst, count=len(lst), size=count)
    if "nextBackwardToken" in resp:
        data["backward"] = resp["nextBackwardToken"]
        data["forword"] = resp["nextForwardToken"]
    return rv.restResult(request, data)

@rd.urlPOST('cloudwatch/log')
@rd.perm_required('view_logs')
@rd.requires_params(["log_group", "log_stream", "event"])
def cloudwatch_log_groups(request):
    log_group = request.DATA.get("log_group")
    log_stream = request.DATA.get("log_stream")
    event = request.DATA.get("event")
    resp = cloudwatch.logToCloudWatch(event, log_group, log_stream)
    return rv.restResult(request, dict(status=True, data=resp))


@rd.urlGET('cloudwatch/log')
@rd.perm_required('cloudwatch')
@rd.requires_params(["log_group", "log_stream"])
def cloudwatch_log_groups(request):
    log_group = request.DATA.get("log_group")
    log_stream = request.DATA.get("log_stream")
    pattern = request.DATA.get("pattern")
    if pattern:
        start = request.DATA.get("dr_start", "6d")
        end = request.DATA.get("dr_end", field_type=datetime)
        resp = cloudwatch.filter(log_group, [log_stream], pattern,
                                 start_time=start, end_time=end,
                                 resp_format=request.DATA.get("format"))
    else:
        resp = cloudwatch.get(log_group, log_stream)
    lst = resp["events"]
    data = dict(status=True, data=lst, count=len(lst))
    if "nextBackwardToken" in resp:
        data["backward"] = resp["nextBackwardToken"]
        data["forword"] = resp["nextForwardToken"]
    data = dict(status=True, data=lst, count=len(lst))
    return rv.restResult(request, data)


@rd.urlGET('cloudwatch/groups')
@rd.perm_required('cloudwatch')
def cloudwatch_log_groups(request):
    return rv.restList(request, cloudwatch.getLogGroups(request.DATA.get("graph", None) is None))


@rd.urlPOST('cloudwatch/insights/start')
@rd.perm_required('cloudwatch')
@rd.requires_params(["log_groups"])
def cloudwatch_insights_start(request):
    log_groups = request.DATA.get("log_groups")
    log_streams = request.DATA.get("log_streams")
    start = request.DATA.get("dr_start", "6h")
    end = request.DATA.get("dr_end", field_type=datetime)
    ip = request.DATA.get("ip")
    text = request.DATA.get("text")
    query = request.DATA.get("query")
    if ip is None and text is None and query is None:
        return rv.restPermissionDenied(request)
    resp = cloudwatch.startSearch(log_groups, start, end, 
                                      ip=ip, text=text, query_string=query,
                                      log_streams=log_streams)
    return rv.restResult(request, dict(status=True, data=resp))


@rd.urlGET(r'cloudwatch/insights/results')
@rd.perm_required('cloudwatch')
@rd.requires_params(["query_id"])
def cloudwatch_insights_results(request):
    query_id = request.DATA.get("query_id")
    results = cloudwatch.getInsightResults(query_id, request.DATA.get("format"))
    return rv.restResult(request, results)

