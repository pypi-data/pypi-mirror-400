from django.db import models
from rest import settings

from rest.models import RestModel, MetaDataModel, MetaDataBase
from rest.fields import JSONField
from objict import nobjict
from rest import crypto
from ws4redis import client as redis
from account.models import Member
import importlib
import metrics

import traceback

import time
from datetime import datetime, timedelta
NOT_FOUND = "-NOT-FOUNT-"

TASK_STATE_SCHEDULED = 0
TASK_STATE_STARTED = 1
TASK_STATE_RETRY = 2
TASK_STATE_COMPLETED = 10
TASK_STATE_FAILED = -1
TASK_STATE_CANCELED = -2

TASK_STATES = [
    (TASK_STATE_SCHEDULED, 'scheduled'),
    (TASK_STATE_STARTED, 'started'),
    (TASK_STATE_RETRY, 'retry_later'),
    (TASK_STATE_COMPLETED, 'completed'),
    (TASK_STATE_FAILED, 'failed'),
    (TASK_STATE_CANCELED, 'canceled')
]

TQ_RETRY_BACKOFF_FACTOR = settings.get("TQ_RETRY_BACKOFF_FACTOR", 2)
TQ_RETRY_ATTEMPTS = settings.get("TQ_RETRY_ATTEMPTS", 5)
TQ_RETRY_DELAY = settings.get("TQ_RETRY_DELAY", 60)
TQ_METRICS = settings.get("TQ_METRICS", True)
TQ_METRICS_GRANULARITY = settings.get("TQ_METRICS_GRANULARITY", "hourly")
TQ_METRICS_CREATED = settings.get("TQ_METRICS_CREATED", False)
TQ_METRICS_FUNCTION = settings.get("TQ_METRICS_FUNCTION", False)
TQ_METRICS_CHANNEL = settings.get("TQ_METRICS_CHANNEL", False)


def getAppHandler(app_name, fname):
    try:
        # module = __import__(app_name + '.tq', globals(), locals(), ['*'], 0)
        module = importlib.import_module(app_name + '.tq')

    except ImportError as err:
        return None

    if hasattr(getattr(module, fname, None), '__call__'):
        return getattr(module, fname)
    return None


class Task(models.Model, RestModel):
    """
    This is the state of a remote task.  This model is a backup store to a task that was scheduled
    via Task.Publish(data)
    TQ_SUBSCRIBE = ["tq_web_request", "tq_model_handler", "tq_app_handler"]

    tq_model_handler is a method on a django Model
    tq_app_handler is a method in a modules tq module... example (mymodule.tq.on_tq_test)

    Extends:
        models.Model
        RestModel
    """
    class RestMeta:
        DEFAULT_SORT = "-modified"
        POST_SAVE_FIELDS = ["action"]
        SEARCH_FIELDS = ["channel", "model", "fname", "data"]
        VIEW_PERMS = ["tq_view"]
        SEARCH_TERMS = [
            "channel", "model", "fname",
            "data", "reason", "runtime", "state"
        ]
        GRAPHS = {
            "list": {
                "fields":[
                    'id',
                    'created',
                    'modified',
                    'started_at',
                    'completed_at',
                    'stale_after',
                    'scheduled_for',
                    'cancel_requested',
                    'state',
                    'runtime',
                    'current_runtime',
                    'channel',
                    'model',
                    'attempts',
                    'fname',
                    ('truncate_data', 'data'),
                    'reason',
                    '_started',
                ],
                "extra": [("get_state_display", "state_display")],
            },
            "default": {
                "extra": [("get_state_display", "state_display")],
            },
            "detailed": {
                "extra": [("get_state_display", "state_display")],
            },
        }
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(default=None, null=True, blank=True)
    completed_at = models.DateTimeField(default=None, null=True, blank=True)
    stale_after = models.DateTimeField(default=None, null=True, blank=True)
    scheduled_for = models.DateTimeField(default=None, null=True, blank=True, db_index=True)
    cancel_requested = models.BooleanField(default=False, blank=True)
    state = models.IntegerField(db_index=True, default=TASK_STATE_SCHEDULED, choices=TASK_STATES)
    runtime = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    channel = models.CharField(max_length=200, db_index=True, default="tq_task")
    model = models.CharField(max_length=200, db_index=True)
    fname = models.CharField(max_length=200, default=None, null=True, blank=True)
    data = JSONField(default=None, null=True, blank=True)
    reason = models.CharField(max_length=255, default=None, null=True, blank=True)
    _started = 0

    @property
    def is_stale(self):
        if not self.stale_after:
            return False
        return self.stale_after <= datetime.now()

    @property
    def truncate_data(self):
        if self.data and self.data.data:
            temp = self.data
            temp.data = "...truncated..."
            return temp
        return self.data

    @property
    def created_age(self):
        return (datetime.now() - self.created).total_seconds()

    @property
    def modified_age(self):
        return (datetime.now() - self.modified).total_seconds()

    @property
    def current_runtime(self):
        if self.state in [10, -1]:
            return self.runtime
        if not self.started_at:
            return self.runtime
        return (datetime.now() - self.started_at).total_seconds()

    @property
    def max_attempts(self):
        if self.data:
            return self.data.get("retry_max_attempts", TQ_RETRY_ATTEMPTS)
        return TQ_RETRY_ATTEMPTS

    def set_action(self, value):
        if value == "retry_now":
            self.retry_now()
        elif value == "cancel":
            request = self.getActiveRequest()
            self.reason = f"cancel request by {request.member.username}"
            self.cancel(request.DATA.get("reason", f"canceled by {request.member.username}"))

    # def auditlog(self, action, message, request=None, path=None, component="taskqueue.Task"):
    #     # message, level=0, request=None, component=None, pkey=None, action=None, group=None, path=None, method=None
    #     # PersistentLog.log(message=message, level=1, action=action, request=request, component=component, pkey=self.pk, path=path, method=self.fname)
    #     raise Exception("auditlog called but is not supported")

    def log(self, text, kind="info"):
        TaskLog.Log(self, text, kind=kind)
        if self.data and ((self.data.log_component and self.data.log_pk) or self.data.log_tid):
            PLOG = self.getModel("auditlog", "PersistentLog")
            level = 0
            if kind == "exception":
                level = 21
            elif kind == "error":
                level = 17
            PLOG.log(message=text, action=f"taskqueue_{kind}",
                     level=level,
                     method=self.fname, path=self.model,
                     tid=self.data.log_tid,
                     component=self.data.log_component,
                     pkey=self.data.log_pk,
                     group=self.data.group_id)

    def log_exception(self, text, kind="exception"):
        self.log(str(text), kind=kind)
        self.log(traceback.format_exc(), "exception")

    def started(self):
        self.state = TASK_STATE_STARTED
        self.started_at = datetime.now()
        self._started = time.time()
        self.attempts += 1
        self.save()

    def retry_later(self, reason=None, from_now_secs=None):
        if reason:
            self.reason = reason
        if from_now_secs == -1:
            # allow backoff retry
            if self.data:
                bof = self.data.get("retry_bof", TQ_RETRY_BACKOFF_FACTOR)
                delay = self.data.get("retry_delay", TQ_RETRY_DELAY)
            else:
                bof = TQ_RETRY_BACKOFF_FACTOR
                delay = TQ_RETRY_DELAY
            attempts = self.attempts - 2
            if attempts == -1:
                # retry first attempt right away
                from_now_secs = 1
            else:
                from_now_secs = delay * (bof ** attempts)
        if from_now_secs is not None:
            # this will not run the task again until after this time has been hit
            self.scheduled_for = datetime.now() + timedelta(seconds=from_now_secs)
        self.state = TASK_STATE_RETRY
        self.cancel_requested = False
        self.save()

    def retry_now(self):
        self.state = TASK_STATE_SCHEDULED
        self.cancel_requested = False
        self.save()
        self.publish()

    def completed(self):
        self.completed_at = datetime.now()
        self.runtime = int(time.time() - self._started)
        self.state = TASK_STATE_COMPLETED
        self.save()
        if TQ_METRICS:
            metrics.metric("tq_task_completed", min_granularity=TQ_METRICS_GRANULARITY)
            if TQ_METRICS_CHANNEL:
                metrics.metric(f"tq_chan_done_{self.channel}", category="tq_chan_done", min_granularity=TQ_METRICS_GRANULARITY)
            if TQ_METRICS_FUNCTION:
                metrics.metric(f"tq_func_done_{self.fname}", category="tq_func_done", min_granularity=TQ_METRICS_GRANULARITY)

    def failed(self, reason=None, category="taskqueue_errors"):
        if reason and len(reason) > 250:
            reason = reason[:250]
        self.reason = reason
        self.state = TASK_STATE_FAILED
        self.notifyError(category=category, reason=reason)
        self.save()
        if TQ_METRICS:
            metrics.metric("tq_task_failed", min_granularity=TQ_METRICS_GRANULARITY)
            if TQ_METRICS_CHANNEL:
                metrics.metric(f"tq_chan_fail_{self.channel}", category="tq_chan_fail", min_granularity=TQ_METRICS_GRANULARITY)
            if TQ_METRICS_FUNCTION:
                metrics.metric(f"tq_func_fail_{self.fname}", category="tq_func_fail", min_granularity=TQ_METRICS_GRANULARITY)

    def notifyError(self, category="taskqueue_errors", reason=None):
        handler = f"{self.model}.{self.fname}"
        subject = f"TaskQueue - {handler}"
        if reason is None:
            reason = self.reason

        msg = f"{handler}<br>\n{reason}"
        metadata = {
            "server": settings.get("HOSTNAME", "unknown"),
            "task": self.pk,
            "reason": reason,
            "app": self.model,
            "fname": self.fname,
            "channel": self.channel,
            "attempts": self.attempts,
            "handler": handler
        }

        if self.data:
            if self.data.url:
                metadata["url"] = self.data.url
                from urllib.parse import urlparse
                purl = urlparse(self.data.url)
                metadata["host"] = purl.netloc
                msg = f"{msg}<br>\n{self.data.url}"
            if self.data.log_component:
                metadata["component"] = self.data.log_component
            if self.data.log_pk:
                metadata["component_id"] = self.data.log_pk
        try:
            import incident
            incident.event_now(
                category, description=subject, details=msg,
                level=3, **metadata)
        except Exception as err:
            self.log(str(err), kind="error")

    def cancel(self, reason=None):
        self.cancel_requested = True
        self.save()
        out = nobjict()
        out.reason = reason
        out.pk = self.pk
        return redis.publish("tq_cancel", out)

    def publish(self, channel=None):
        out = nobjict()
        out.pk = self.pk
        out.model = self.model
        out.fname = self.fname
        out.data = self.data
        if not channel:
            channel = self.channel
        if TQ_METRICS and TQ_METRICS_CREATED:
            metrics.metric("tq_task_created", min_granularity=TQ_METRICS_GRANULARITY)
        return redis.publish(channel, out)

    def getHandler(self):
        if "." not in self.model:
            return getAppHandler(self.model, self.fname)
        app, mname = self.model.split('.')
        model = self.restGetModel(app, mname)
        if not model:
            return None
        return getattr(model, self.fname, None)

    @classmethod
    def WebRequest(cls, url, data, fname="POST", stale_after_seconds=0,
                   log_component=None, log_pk=None, log_tid=None):
        tdata = nobjict()
        tdata.url = url
        tdata.data = data
        if log_component is not None:
            tdata.log_component = log_component
            tdata.log_pk = log_pk
        if log_tid is not None:
            tdata.log_tid = log_tid
        task = cls(channel="tq_hook", model="tq_web_request", fname=fname, data=tdata)
        if stale_after_seconds:
            task.stale_after = datetime.now() + timedelta(seconds=stale_after_seconds)
        task.save()
        task.publish()
        return task

    @classmethod
    def EmailRequest(cls, address, data, filename=None, subject=None,
                     log_component=None, log_pk=None, log_tid=None):
        tdata = nobjict()
        tdata.address = address
        tdata.filename = filename
        tdata.subject = subject
        tdata.data = data
        if log_component is not None:
            tdata.log_component = log_component
            tdata.log_pk = log_pk
        if log_tid is not None:
            tdata.log_tid = log_tid
        task = cls(channel="tq_hook", model="tq_email_request", data=tdata)
        task.save()
        task.publish()
        return task

    @classmethod
    def SMSRequest(cls, phone, data, log_component=None, log_pk=None, log_tid=None):
        tdata = nobjict()
        tdata.phone = phone
        tdata.data = data
        if log_component is not None:
            tdata.log_component = log_component
            tdata.log_pk = log_pk
        if log_tid is not None:
            tdata.log_tid = log_tid
        task = cls(channel="tq_hook", model="tq_sms_request", data=tdata)
        task.save()
        task.publish()
        return task

    @classmethod
    def SFTPRequest(cls, host, data, filename, username, password,
                    log_component=None, log_pk=None, log_tid=None):
        tdata = nobjict()
        tdata.host = host
        tdata.filename = filename
        # TODO this should be more secure!
        # TODO support ssh keys?
        tdata.username = username
        tdata.password = password
        tdata.data = data
        if log_component is not None:
            tdata.log_component = log_component
            tdata.log_pk = log_pk
        if log_tid is not None:
            tdata.log_tid = log_tid
        task = cls(channel="tq_hook", model="tq_sftp_request", data=tdata)
        task.save()
        task.publish()
        return task

    @classmethod
    def S3Request(cls, bucket, data, folder, aws, secret, filename, when,
                  log_component=None, log_pk=None, log_tid=None):
        tdata = nobjict()
        tdata.bucket = bucket
        tdata.filename = filename
        tdata.data = data
        tdata.folder = folder
        tdata.aws = aws
        tdata.secret = secret
        tdata.when = str(when)
        if log_component is not None:
            tdata.log_component = log_component
            tdata.log_pk = log_pk
        if log_tid is not None:
            tdata.log_tid = log_tid
        task = cls(channel="tq_hook", model="tq_s3_request", data=tdata)
        task.save()
        task.publish()
        return task

    @classmethod
    def PublishModelTask(cls, model_name, fname, data, stale_after_seconds=0, channel="tq_model_handler", scheduled_for=None):
        return cls.Publish(cls, model_name, fname, data, stale_after_seconds, channel, scheduled_for)

    @classmethod
    def Publish(cls, app_name, fname, data=None, stale_after_seconds=0, channel="tq_app_handler", scheduled_for=None):
        # tq_handler will check for a function in the django app tq.py
        task = cls(model=app_name, fname=fname, data=data, channel=channel, scheduled_for=scheduled_for)
        if stale_after_seconds:
            task.stale_after = datetime.now() + timedelta(seconds=stale_after_seconds)
        if scheduled_for is not None:
            # this means we just save as a retry, and let it be scheduled for later
            task.state = TASK_STATE_RETRY
            task.save()
            return task
        task.save()
        task.publish(channel)
        return task

    @classmethod
    def FromEvent(cls, event):
        if not event.data or not event.data.pk:
            return None
        return cls.objects.filter(pk=event.data.pk).last()

    @classmethod
    def PublishTest(cls, count=1, sleep_time=20.0):
        for i in range(1, count+1):
            cls.Publish("taskqueue", "on_tq_test", {"published_at": time.time(), "index":i, "sleep_time": sleep_time})

    @classmethod
    def RestartEngine(cls):
        redis.publish("tq_restart", {})


class TaskWorkerClient:
    def __init__(self, hostname, **kwargs):
        self.hostname = hostname
        uid = crypto.randomString(16)
        self.recv_channel = f"tq:{uid}:{settings.HOSTNAME}"
        self.send_channel = f"tq:host:{hostname}"
        self.client = None
        self.pubsub = None

    def connect(self):
        if self.client is None:
            self.client = redis.getRedisClient()
            self.pubsub = self.client.pubsub()
            self.pubsub.subscribe(self.recv_channel)
            self.pubsub.get_message(timeout=2.0)  # wait for subscription

    def close(self):
        if self.client is not None:
            self.pubsub.unsubscribe(self.recv_channel)
            self.client = None
            self.pubsub = None

    def send(self, data):
        self.connect()
        data["hostname"] = settings.HOSTNAME
        data["response_channel"] = self.recv_channel
        redis.publish(
            self.send_channel,
            data, self.client)

    def recv(self, timeout=5.0):
        self.connect()
        msg = self.pubsub.get_message(timeout=timeout)
        if msg is None:
            raise Exception("no response")
        msg = nobjict.fromdict(msg)
        if msg.data:
            msg.data = nobjict.fromJSON(msg.data)
        return msg.data

    def ping(self):
        start = time.perf_counter()
        self.send(dict(action="ping"))
        try:
            response = self.recv()
        except Exception as err:
            response = nobjict(action="error", error=str(err))
        response.time = time.perf_counter() - start
        return response.action == "pong", response

    def get_stats(self):
        return self.send_and_recv("get_stats")

    def restart(self):
        return self.send_and_recv("restart")

    def send_and_recv(self, action):
        start = time.perf_counter()
        self.send(dict(action=action))
        try:
            response = self.recv()
        except Exception as err:
            response = nobjict(action="error", error=str(err))
        response.time = time.perf_counter() - start
        return response

    @classmethod
    def PING(cls, hostname):
        client = TaskWorkerClient(hostname)
        client.connect()
        status, msg = client.ping()
        client.close()
        return status, msg

    @classmethod
    def GET_STATS(cls, hostname):
        client = TaskWorkerClient(hostname)
        client.connect()
        msg = client.get_stats()
        client.close()
        return msg

    @classmethod
    def GET_ONLINE(cls):
        return [h.decode() for h in redis.smembers("tq:host:online")]


class TaskLog(models.Model, RestModel):
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    task = models.ForeignKey(Task, related_name="logs", on_delete=models.CASCADE)
    kind = models.CharField(max_length=64, default=None, null=True, blank=True)
    text = models.TextField()

    @classmethod
    def Log(cls, task, text, kind="info"):
        log = cls(task=task, text=text, kind=kind)
        log.save()
        return log


class TaskHook(models.Model, RestModel, MetaDataModel):
    """
    This does nothing on its own.  It simply allows for the defining of task hooks
    that can be used during execution of ones own task logic.  The task logic would
    look up the group and channel (just a unique identifier for when the hook is caught)

    use properties to add extra metadata for this hook.
        - group     group this hook belongs to
        - kind      HTTP_POST, EMAIL, SMS, SFTP
        - data_format    file format, csv, json, pdf
        - endpoint  web address, email, sms or other
        - channel   a unique keyword to use to search when looking for the hook
        - model     django app.Model string to use to search when looking for
    """
    class RestMeta:
        CAN_DELETE = True
        DEFAULT_SORT = "-modified"
        SEARCH_FIELDS = ["channel", "model", "endpoint"]
        VIEW_PERMS = ["tq_view"]
        SEARCH_TERMS = [
            "channel", "model", "fname",
            "data", "reason", "runtime", "state"
        ]
        GRAPHS = {
            "list": {
                "extra":["metadata"],
                "graphs": {
                    "group":"basic"
                }
            },
            "default": {
                "extra":["metadata"],
                "graphs": {
                    "group":"basic"
                }
            },
            "detailed": {
                "graphs": {
                    "self":"default"
                }
            },
        }

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    group = models.ForeignKey("account.Group", blank=True, null=True, default=None, related_name="+", on_delete=models.CASCADE)
    kind = models.CharField(max_length=200, blank=True, null=True)
    data_format = models.CharField(max_length=32, default="json")
    endpoint = models.CharField(max_length=200, blank=True, null=True)
    state = models.IntegerField(default=1, choices=[(0, 'inactive'), (1, 'active')], db_index=True)

    # channel is just a unique keyword to check for hooks
    channel = models.CharField(max_length=200, db_index=True, default="tq_hook")
    # if this only gets fired for a particular model
    model = models.CharField(max_length=200, blank=True, null=True, db_index=True)

    def trigger(self, data, when=None):
        task = None
        if self.kind == "HTTP_POST":
            # url, data, fname="POST", stale_after_seconds=0
            task = Task.WebRequest(self.endpoint, data)
        elif self.kind == "HTTP_GET":
            task = Task.WebRequest(self.endpoint, data, fname='GET')
        elif self.kind == "EMAIL":
            task = Task.EmailRequest(
                self.endpoint, data,
                self.getProperty("filename", "{date.month:02d}{date.day:02d}{date.year}." + self.data_format),
                self.getProperty("subject", "{date.month:02d}{date.day:02d}{date.year}"))
        elif self.kind == "SFTP":
            task = Task.SFTPRequest(
                self.endpoint, data,
                self.getProperty("filename", "{date.month:02d}{date.day:02d}{date.year}." + self.data_format),
                self.getProperty("username"),
                self.getProperty("password"))
        elif self.kind == "SMS":
            task = Task.SMSRequest(self.endpoint, data)
        elif self.kind == "S3":
            task = Task.S3Request(
                self.getProperty("bucket"), data,
                self.getProperty("folder", None),
                self.getProperty("aws", None),
                self.getProperty("secret", None),
                self.getProperty("filename", "{date.month:02d}{date.day:02d}{date.year}." + self.data_format),
                when)
        else:
            print("unknown hook kind: {}".format(self.kind))
        return task


class TaskHookMetaData(MetaDataBase):
    parent = models.ForeignKey(TaskHook, related_name="properties", on_delete=models.CASCADE)
