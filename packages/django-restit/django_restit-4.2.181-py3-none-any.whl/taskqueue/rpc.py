from rest import views as rv
from rest import decorators as rd
from rest import search
from rest import helpers as rh
from rest.uberdict import UberDict
from datetime import datetime, timedelta
from taskqueue import models as tq 

from django.db.models import Sum, Max, Count, Q
from django.db.models.functions import Trunc


@rd.url(r'^task$')
@rd.url(r'^task/(?P<pk>\d+)$')
@rd.login_required
def rest_on_task(request, pk=None):
    return tq.Task.on_rest_request(request, pk)


@rd.url(r'^task/log$')
@rd.url(r'^task/log/(?P<pk>\d+)$')
@rd.login_required
def rest_on_tasklog(request, pk=None):
    return tq.TaskLog.on_rest_request(request, pk)


@rd.url(r'^task/schedule$')
@rd.url(r'^task/schedule/(?P<pk>\d+)$')
@rd.login_required
def rest_on_tasklog_schedule(request, pk=None):
    return tq.ScheduledTask.on_rest_request(request, pk)


@rd.urlPOST(r'^task/publish$')
@rd.perm_required(["manage_users", "tq_publish"])
def rest_on_task_publish(request, pk=None):
    app = request.DATA.get("app").strip()
    module = request.DATA.get("module").strip()
    task_data = request.DATA.get("task_data").strip()
    if not app or not module:
        return rv.restStatus(request, False, error="Both app and module are required.")
    task = tq.Task.Publish(app, module, task_data)
    return rv.restGet(request, task, **tq.Task.getGraph("default"))


@rd.url(r'^task/hook$')
@rd.url(r'^task/hook/(?P<pk>\d+)$')
@rd.login_required
def rest_on_tasklog(request, pk=None):
    return tq.TaskHook.on_rest_request(request, pk)


@rd.url(r'^task/hook/test$')
@rd.perm_required("manage_hooks")
def rest_on_task_hook_test(request):
    hook = request.DATA.get("hook", None)
    if not hook:
        return rv.restStatus(request, False, error="Hook attributes required.")
    data = request.DATA.get("data", None)
    when = request.DATA.get("when", None)
    props = request.DATA.get("props", None)
    category = request.DATA.get("category", None)
    hook = tq.TaskHook(**hook)
    if props:
        hook.save()
        hook.setProperties(props, category=category)
        task = hook.trigger(data, when)
        hook.delete()
    else:
        task = hook.trigger(data, when)
    return rv.restGet(request, task, **tq.Task.getGraph("default"))


@rd.url(r'^restart$')
@rd.perm_required("manage_staff")
def rest_on_restart(request):
    rh.log_print("{} request task engine restart".format(request.member.username))
    tq.Task.RestartEngine()
    return rv.restStatus(request, True)


@rd.url(r'^test$')
@rd.perm_required("manage_staff")
def rest_on_test(request):
    tq.Task.PublishTest(request.DATA.get("test_count", 1, field_type=int), request.DATA.get("sleep_time", 10.0, field_type=float))
    return rv.restStatus(request, True)


@rd.url(r'^task/status$')
@rd.login_required
def rest_on_task_status(request):
    out = UberDict()
    last_completed = tq.Task.objects.filter(state=tq.TASK_STATE_COMPLETED).last()
    if last_completed:
        out.last_completed = last_completed.completed_at
    last_scheduled = tq.Task.objects.all().last()
    if last_scheduled:
        out.last_scheduled = last_scheduled.created
    stale = datetime.now() - timedelta(minutes=request.DATA.get("minutes_back", 60))
    qset = tq.Task.objects.filter(modified__gte=stale)
    status = qset.aggregate(
        retry=Count('state', filter=Q(state=tq.TASK_STATE_RETRY)),
        completed=Count('state', filter=Q(state=tq.TASK_STATE_COMPLETED)),
        failed=Count('state', filter=Q(state=tq.TASK_STATE_FAILED)),
        running=Count('state', filter=Q(state=tq.TASK_STATE_STARTED)),
        backlog=Count('state', filter=Q(state=tq.TASK_STATE_SCHEDULED)))
    status["total"] = qset.count()
    out.update(status)
    return rv.restGet(request, out)


@rd.urlGET('workers')
@rd.login_required
def rest_on_runners(request):
    workers = tq.TaskWorkerClient.GET_ONLINE()
    if request.DATA.get("graph") == "detailed":
        output = []
        for r in workers:
            stats = tq.TaskWorkerClient.GET_STATS(r)
            stats.id = r
            output.append(stats)
        workers = output
    return rv.restReturn(request, dict(data=workers))


# write a django query to 

@rd.url(r'^task/stats$')
@rd.login_required
def rest_on_stats(request):
    now = datetime.now() 
    when = now - timedelta(days=request.DATA.get("days", 7, field_type=int))
    qset = tq.Task.objects.filter(
        created__gte=when)
    reports = list(
        qset
        .annotate(day=Trunc('created', 'day'))
        .values('day')
        .annotate(completed=Count('state', filter=Q(state=10)))
        .annotate(failed=Count('state', filter=Q(state=-1)))
        .annotate(longest=Max('runtime')))
    output = []
    
    when = when.replace(hour=0, minute=0, second=0)
    while when < now:
        dr = None
        for r in reports:
            day = r["day"]
            if day.day == when.day and day.month == when.month:
                dr = r
                break
        if dr is not None:
            output.append(dr)
        else:
            output.append(dict(day=when, completed=0, failed=0, longest=0))
        when += timedelta(days=1)

    status = qset.aggregate(
        retry=Count('state', filter=Q(state=tq.TASK_STATE_RETRY)),
        completed=Count('state', filter=Q(state=tq.TASK_STATE_COMPLETED)),
        failed=Count('state', filter=Q(state=tq.TASK_STATE_FAILED)),
        running=Count('state', filter=Q(state=tq.TASK_STATE_STARTED)),
        backlog=Count('state', filter=Q(state=tq.TASK_STATE_SCHEDULED)))
    return rv.restGet(request, dict(stats=output, status=status))


@rd.url(r'^test/webrequest$')
def rest_on_webrequest(request):
    msg = "Successfully received the following data\n{}".format(str(request.DATA.toDict()))
    return rv.restStatus(request, True, msg=msg)
