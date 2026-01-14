"""
This is where you can put handlers for running async background tasks

Task.Publish("myapp", "on_tq_test")
"""
from datetime import datetime, timedelta
from auditlog.models import PersistentLog
from sessionlog.models import SessionLog
from rest import settings

AUDITLOG_PRUNE_DAYS = settings.get("AUDITLOG_PRUNE_DAYS", 90)
REST_LOG_PRUNE_DAYS = settings.get("REST_LOG_PRUNE_DAYS", 90)
ACCOUNT_LOG_PRUNE_DAYS = settings.get("ACCOUNT_LOG_PRUNE_DAYS", 640)
ASYNC_LOG_PRUNE_DAYS = settings.get("ASYNC_LOG_PRUNE_DAYS", 14)
SESSION_PRUNE_DAYS = settings.get("SESSION_PRUNE_DAYS", 180)

ACCOUNT_LOG_COMPONENTS = settings.get("ACCOUNT_LOG_COMPONENTS", ["account.Member", "account.Group"])


def on_cleanup(task):
    # cleanup log files in the var directory
    count = cleanupAuditLogs()
    if count > 0:
        task.log(f"deleted {count} audit logs")

    count = cleanupAsyncLogs()
    if count > 0:
        task.log(f"deleted {count} async logs")

    count = cleanupRestLogs()
    if count > 0:
        task.log(f"deleted {count} rest logs")

    count = cleanupAccountLogs()
    if count > 0:
        task.log(f"deleted {count} account logs")

    count = cleanupSessionLogs()
    if count > 0:
        task.log(f"deleted {count} session logs")


def cleanupAuditLogs():
    if AUDITLOG_PRUNE_DAYS:
        before = datetime.now() - timedelta(days=AUDITLOG_PRUNE_DAYS)
        return PersistentLog.objects.filter(when__lte=before).exclude(component__in=ACCOUNT_LOG_COMPONENTS).delete()[0]
    return 0


def cleanupRestLogs():
    if REST_LOG_PRUNE_DAYS:
        before = datetime.now() - timedelta(days=REST_LOG_PRUNE_DAYS)
        return PersistentLog.objects.filter(when__lte=before, component__in=["rest", "action"]).exclude(component__in=ACCOUNT_LOG_COMPONENTS).delete()[0]
    return 0


def cleanupAccountLogs():
    if ACCOUNT_LOG_PRUNE_DAYS:
        before = datetime.now() - timedelta(days=ACCOUNT_LOG_PRUNE_DAYS)
        return PersistentLog.objects.filter(when__lte=before, component__in=ACCOUNT_LOG_COMPONENTS).delete()[0]
    return 0


def cleanupAsyncLogs():
    if ASYNC_LOG_PRUNE_DAYS:
        before = datetime.now() - timedelta(days=ASYNC_LOG_PRUNE_DAYS)
        return PersistentLog.objects.filter(when__lte=before, action="async").delete()[0]
    return 0


def cleanupSessionLogs():
    SessionLog.objects.filter()
    before = datetime.now() - timedelta(days=SESSION_PRUNE_DAYS)
    return SessionLog.objects.filter(created__lte=before).delete()[0]
