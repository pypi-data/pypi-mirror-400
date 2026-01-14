from rest.decorators import periodic
from taskqueue.models import Task
from rest import settings


@periodic(hour=settings.get("AUDITLOG_CRON_HOUR", 9), minute=settings.get("AUDITLOG_CRON_MINUTE", 45))
def run_log_cleanup(force=False, verbose=False, now=None):
    # schedule pruning
    Task.Publish("auditlog", "on_cleanup", channel="tq_app_handler_cleanup")


