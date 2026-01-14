

from rest.decorators import periodic, PERIODIC_EVERY_5_MINUTES
from rest import helpers
from rest.log import getLogger
from taskqueue.models import Task, TASK_STATE_COMPLETED, TASK_STATE_RETRY, TASK_STATE_SCHEDULED
from django.db.models import Q
from account.models import Member
from datetime import datetime, timedelta
import incident

import os

from rest import settings

logger = getLogger()

PID_FILE = os.path.join(settings.VAR_ROOT, "tq_worker.pid")
ENGINE_CMD = os.path.join(settings.BIN_ROOT, "tq_worker.py")

TQ_SUBSCRIBE = settings.get("TQ_SUBSCRIBE", [])
TQ_REPORT_BACKLOG = settings.get("TQ_REPORT_BACKLOG", 20)
TQ_DELETE_AFTER = settings.get("TQ_DELETE_AFTER", 30)
TQ_DELETE_COMPLETED_AFTER = settings.get("TQ_DELETE_COMPLETED_AFTER", 7)

# allow setting the periodic retry to either 5minutes or 1minute
TQ_RETRY_FREQ = settings.get("TQ_RETRY_FREQ", 5)
if TQ_RETRY_FREQ == 5:
    TQ_RETRY_FREQ = PERIODIC_EVERY_5_MINUTES
else:
    TQ_RETRY_FREQ = None


def isLocalEngineRunning():
    pid = helpers.getPidFromFile(PID_FILE)
    if not pid:
        return False
    return helpers.isPidRunning(pid)


def startLocalEngine():
    # needs to be added to sudoers
    helpers.sudoCMD([ENGINE_CMD, "start"], as_user="www")


@periodic()
def run_check_taskrunner(force=False, verbose=False, now=None):
    # check if pid is running
    # check if any backlog exists (ignore state=1)
    if not TQ_SUBSCRIBE:
        logger.warning("periodic taskrunner called but engine is disabled via empty TQ_SUBSCRIBE")
        return
    if not isLocalEngineRunning():
        # attempt to start local engine
        logger.info("pid is: {} @ {}".format(helpers.getPidFromFile(PID_FILE), PID_FILE))
        logger.info("taskrunner is not running? starting task runner...")
        startLocalEngine()


@periodic(minute=TQ_RETRY_FREQ)
def run_retry(force=False, verbose=False, now=None):
    # check for retry jobs, but only on the master
    if not settings.TQ_MASTER:
        return

    if now is None:
        now = datetime.now()
    retry_jobs = Task.objects.filter(state=TASK_STATE_RETRY).filter(Q(scheduled_for__isnull=True)|Q(scheduled_for__lte=now))[:200]
    for retry in retry_jobs:
        if not retry.is_stale:
            retry.retry_now()
        else:
            retry.failed("stale")


@periodic(minute=PERIODIC_EVERY_5_MINUTES)
def run_checkup(force=False, verbose=False, now=None):
    if not settings.TQ_MASTER:
        return
    # check if we have back log
    qset = Task.objects.filter(state=TASK_STATE_SCHEDULED)
    backlog_count = qset.count()
    # btask = Task.objects.filter(state=TASK_STATE_SCHEDULED).last()
    if backlog_count > TQ_REPORT_BACKLOG:
        details = ""
        for key, value in helpers.countOccurences(qset, "channel").items():
            details += "{} = {}\n".format(key, value)
        incident.event_now(
            "taskqueue_errors", f"Task Queue Backlog of {backlog_count}",
            details=details, level=3)


@periodic(minute=45, hour=10)
def run_cleanup(force=False, verbose=False, now=None):
    if not settings.TQ_MASTER:
        return
    stale = datetime.now() - timedelta(days=TQ_DELETE_AFTER)
    count = Task.objects.filter(created__lte=stale).delete()[0]
    if count:
        logger.info("deleted {} old tasks".format(count))
    stale = datetime.now() - timedelta(days=TQ_DELETE_COMPLETED_AFTER)
    count = Task.objects.filter(created__lte=stale, state=TASK_STATE_COMPLETED).delete()[0]
    if count:
        logger.info("deleted {} old completed tasks".format(count))


PUSH_METRICS_TO_CLOUDWATCH = settings.get("PUSH_METRICS_TO_CLOUDWATCH", False)

@periodic(minute=PERIODIC_EVERY_5_MINUTES)
def run_aws_metrics(force=False, verbose=False, now=None):
    if PUSH_METRICS_TO_CLOUDWATCH:
        from metrics.providers import aws
        aws.publishLocalMetrics()
