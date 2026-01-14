"""
This is where you can put handlers for running async background tasks

Task.Publish("myapp", "on_tq_test")
"""
# from datetime import datetime, timedelta
# from auditlog.models import PersistentLog
# from django.conf import settings
from incident import models as ia
from account import models as account
from location.models import GeoIP
from rest import helpers
from rest import settings
from inbox import models as inbox
import time
from datetime import datetime, timedelta
from django.db.models import Q


POSIX_BODY_BREAK = "\n\n\n"
WIN_BODY_BREAK = "\r\n\r\n\r\n"


def new_event(task):
    data = task.data
    if "hostname" in data.metadata:
        data.hostname = data.metadata.hostname
    if "details" in data.metadata:
        data.details = data.metadata.details
    if "component" in data.metadata:
        data.component = data.metadata.component
    if "component_id" in data.metadata:
        data.component_id = data.metadata.component_id
    if "ip" in data.metadata:
        data.reporter_ip = data.metadata.ip
    ia.Event.createFromDict(None, task.data)
    task.completed()


def firewall_block(task):
    # Task.Publish("incident", "firewall_block", {ip:"x.x.x.x"}, channel="tq_broadcast")
    helpers.local_block_ip(task.data.ip, metadata=task.data.metadata)
    task.log(f"{settings.HOSTNAME} - {task.data.ip} BLOCKED")
    task.completed()


def firewall_unblock(task):
    # Task.Publish("incident", "firewall_unblock", {ip:"x.x.x.x"}, channel="tq_broadcast")
    helpers.local_unblock_ip(task.data.ip, metadata=task.data.metadata)
    task.log(f"{settings.HOSTNAME} - {task.data.ip} UNBLOCKED")
    task.completed()


def on_incoming_email(task):
    # dict(pk=msg.pk, to_email=msg.to_email, from_email=msg.from_email)
    msg = inbox.Message.objects.filter(pk=task.data.pk).last()
    if msg is None:
        time.sleep(2.0)
        msg = inbox.Message.objects.filter(pk=task.data.pk).last()
        if msg is None:
            task.failed("could not find message")
            return
    # first we attempt to find the incident id from the subject
    if "#" not in msg.subject:
        task.failed("could not find incident id in subject")
        return
    pk = msg.subject[msg.subject.find("#")+1:]
    if ' ' in pk:
        pk = pk[:pk.find(' ')]
    obj = ia.Incident.objects.filter(pk=int(pk)).last()
    if obj is None:
        task.failed(f"could not find incident #{pk}")
        return
    member = account.Member.objects.filter(email=msg.from_email).last()
    username = msg.from_email
    if member is not None:
        username = member.username
    body = msg.body
    if POSIX_BODY_BREAK in body:
        body = body[:body.find(POSIX_BODY_BREAK)]
    elif WIN_BODY_BREAK in body:
        body = body[:body.find(WIN_BODY_BREAK)]
    lines = body.split("\n")
    note = []
    for line in lines:
        if line.startswith(">"):
            break
        action = line.strip().lower()
        if action in ["close", "closed", "resolve", "resolved", "handled"]:
            obj.state = ia.INCIDENT_STATE_RESOLVED
            obj.save()
            msg = f"resolved by {username}"
            note.append(msg)
            obj.logHistory("history", msg, notify=False)
        elif action in ["open", "accept"]:
            obj.state = ia.INCIDENT_STATE_OPENED
            obj.save()
            msg = f"opened by {username}"
            note.append(msg)
            obj.logHistory("history", msg, notify=False)
        elif action in ["ignore"]:
            obj.state = ia.INCIDENT_STATE_IGNORE
            obj.save()
            msg = f"ignored by {username}"
            note.append(msg)
            obj.logHistory("history", msg, notify=False)
        elif action in ["pause"]:
            obj.state = ia.INCIDENT_STATE_PAUSE
            obj.save()
            msg = f"paused by {username}"
            note.append(msg)
            obj.logHistory("history", msg, notify=False)
        else:
            note.append(line)
    obj.logHistory("email", "\n".join(note), member=member)


def run_cleanup(task):
    stale = datetime.now() - timedelta(days=90)
    # delete all ossec alerts older then 90 days
    count = ia.ServerOssecAlert.objects.filter(created__lte=stale).delete()[0]
    if count:
        task.log(f"deleted {count} old ServerOssecAlert")
    # delete all events older then 90 days
    count = ia.Event.objects.filter(created__lte=stale).filter(
        Q(incident__state=ia.INCIDENT_STATE_IGNORE) | Q(incident__isnull=True)).delete()[0]
    if count:
        task.log(f"deleted {count} old Events")
    
    count = ia.Incident.objects.filter(created__lte=stale, state=ia.INCIDENT_STATE_IGNORE).delete()[0]
    if count:
        task.log(f"deleted {count} old Incidents")

    count = GeoIP.removeDuplicates()
    if count:
        task.log(f"deleted {count} duplicate IPs")


def run_auto_close(task):
    # lets check any incidents that haven't reached action threshold and older then bundle time
    qset = ia.Incident.objects.filter(state=ia.INCIDENT_STATE_PENDING)
    for inc in qset:
        if inc.bundle_expired:
            inc.state = ia.INCIDENT_STATE_IGNORE
            inc.save()
            inc.logHistory("history", "auto ignore", notify=False)

