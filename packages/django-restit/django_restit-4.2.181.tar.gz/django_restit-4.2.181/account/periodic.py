from rest.decorators import periodic
from datetime import datetime, timedelta
from .models import Member, NotificationRecord
from sessionlog.models import SessionLog


@periodic(minute=15)
def run_cleanup_tokens(force=False, verbose=False, now=None):
    # we want to nuke invite tokens every 15 minutes
    # we do not want to do this if using invite
    stale = datetime.now() - timedelta(hours=48)
    qset = Member.objects.filter(auth_code__isnull=False).filter(modified__lte=stale)
    qset.update(auth_code=None)

    # lets prune old non active sessions
    SessionLog.Clean(limit=10000)


@periodic(day=5, hour=11, minute=30)
def run_cleanup_junk(force=False, verbose=False, now=None):
    # cleanup misc data like email notifications
    stale = datetime.now() - timedelta(days=90)
    qset = NotificationRecord.objects.filter(created__lte=stale)
    qset.delete()
