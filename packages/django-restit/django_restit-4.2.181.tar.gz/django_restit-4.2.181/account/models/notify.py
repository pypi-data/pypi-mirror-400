from django.db import models
from rest import settings

from rest.models import RestModel
from rest import mail as rest_mail
from rest import helpers as rh
import inbox.utils

from .member import Member

from datetime import datetime, timedelta
import threading
import incident


def sendEmail(email_to, subject, body=None, attachments=[], 
              from_email=settings.DEFAULT_FROM_EMAIL, background=False):
    record = recordEmail(email_to, subject, body, attachments, from_email)
    record.send(background=background)
    return record


def recordEmail(email_to, subject, body=None, attachments=[], 
                from_email=settings.DEFAULT_FROM_EMAIL):
    email_record = NotificationRecord(
        method="email",
        subject=subject,
        from_addr=from_email,
        body=body)
    email_record.save()
    email_record.addAttachments(attachments)
    if isinstance(email_to, str):
        email_to = [email_to]
    for email in email_to:
        member = Member.objects.filter(email=email).last()
        nr = NotificationMemberRecord(
            member=member, to_addr=email,
            notification=email_record)
        nr.save()
    return email_record


class NotificationRecord(models.Model, RestModel):
    class RestMeta:
        CAN_SAVE = CAN_CREATE = False
        DEFAULT_SORT = "-created"
        SEARCH_FIELDS = ["subject"]
        SEARCH_TERMS = ["subject", ("to", "to__to_addr"), "body", "reason", "state", ("from", "from_addr")]
        GRAPHS = {
            "list": {
                "fields": ["id", ("get_state_display", "state_display"), "created", "subject", "from_addr", "to_emails", "reason", "state", "attempts"],
            },
            "default": {
                "extra": ["to_emails", ("get_state_display", "state_display")]
            }
        }
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified = models.DateTimeField(auto_now=True, editable=False)
    method = models.CharField(max_length=128, default="email", db_index=True)

    from_addr = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    reason = models.TextField()
    # new=0, queued=-5, sent=1
    state = models.IntegerField(default=0, choices=[(0, "new"), (-5, "queued"), (1, "sent"), (-10, "failed")], db_index=True)
    attempts = models.IntegerField(default=0)

    @property
    def to_emails(self):
        return list(self.to.all().values_list("to_addr", flat=True))

    def send(self, member_records=None, background=True):
        email_to = []
        save_records = True
        if not member_records:
            member_records = self.to.all()
            save_records = False
        for r in member_records:
            email_to.append(r.to_addr)
            if save_records:
                r.notification = self
                r.save()
        if NotificationRecord.canSend():
            if background:
                t = threading.Thread(target=self.sendNow, args=[email_to])
                t.start()
            else:
                self.sendNow(email_to)
            return True
        if self.state != -5:
            self.state = -5
            self.save()
        return False

    def sendNow(self, email_to):
        try:
            inbox.utils.send(
                self.from_addr,
                email_to,
                self.subject,
                self.body,
                attachments=self.attachments.all(),
                fail_silently=False)
            # self.reason = "sent"
            self.state = 1
        except Exception as err:
            self.reason = str(err)
            self.attempts += 1
            if self.attempts >= 3:
                self.state = -10
            else:
                self.state = -5
            incident.event_now(
                "email",
                f"error sending email to: {email_to} - {self.subject}",
                level=2,
                subject=self.subject,
                from_addr=self.from_addr,
                to_addr=email_to,
                details=self.reason)
        self.save()
        return True 

    def attach(self, name, mimetype, data):
        atmnt = NotificationAttachment(notification=self, name=name, mimetype=mimetype, data=data)
        atmnt.save()
        return atmnt

    def addAttachments(self, attachments):
        if not attachments:
            return False
        for a in attachments:
            if isinstance(a, str):
                # TODO handle file inport
                pass
            else:
                self.attach(a.name, a.mimetype, a.data)

    @classmethod
    def canSend(cls):
        if not settings.get("THROTTLE_EMAILS", False):
            return True
        max_emails_per_minute = settings.get("MAX_EMAILS_PER_MINUTE", 30)
        last_email = NotificationRecord.objects.filter(state=1).last()
        now = datetime.now()
        if last_email and (now - last_email.created).total_seconds() < 30:
            # we sent an email less then a minute ago
            # now we can to count the number of message sent in last minute
            when = now - timedelta(seconds=60)
            sent = NotificationRecord.objects.filter(state=1, created__gte=when).count()
            return sent < max_emails_per_minute
        return True

    @classmethod
    def notifyFromEmails(cls, emails, subject, message=None,
                         template=None, context=None, email_only=False,
                         sms_msg=None, force=False,
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         attachments=[]):
        # Member = RestModel.getModel("account", "Member")
        members = Member.objects.filter(email__in=emails)
        cls.notify(members, subject, message, template, context, email_only, sms_msg, force, from_email, attachments)


    @classmethod
    def notify(cls, notify_users, subject, message=None, 
               template=None, context=None, email_only=False,
               sms_msg=None, force=False,
               from_email=settings.DEFAULT_FROM_EMAIL,
               attachments=[]):
        dup_list = []
        email_to = []
        sms_to = []
        for member in notify_users:
            via = member.getProperty("notify_via", "all")
            phone = member.getProperty("phone")
            email = member.email
            valid_email = email is not None and "@" in email and "invalid" not in email
            allow_sms = not email_only and phone and (force or via in ["all", "sms"])
            allow_email = not member.email_disabled and valid_email and (force or via in ["all", "email"])
            if not allow_email and not allow_sms:
                continue
            if allow_email and email not in dup_list:
                dup_list.append(email)
                email_to.append(member)
            if not email_only and allow_sms and phone not in dup_list:
                dup_list.append(phone)
                sms_to.append(phone)

        if len(dup_list) == 0:
            return

        if not message and not template and subject:
            message = subject
        if not sms_msg and subject:
            sms_msg = subject
        if not sms_msg and message:
            sms_msg = message

        if subject and len(subject) > 80:
            epos = subject.find('. ') + 1
            if epos > 10:
                subject = subject[:epos]
            if len(subject) > 80:
                subject = subject[:80]
                subject = subject[:subject.rfind(' ')] + "..."

        if sms_to:
            for phone in sms_to:
                SMS.send(phone, sms_msg)

        if not email_to:
            return
        for member in email_to:
            cls._notifyViaEmail(member, subject, message, template, context, attachments, from_email)

    @classmethod
    def _notifyViaEmail(cls, member, subject, message, template, context, 
                        attachments, from_email=settings.DEFAULT_FROM_EMAIL):
        # lets verify the db is working
        if template:
            if context is None:
                context = {}
            if message is not None:
                context["body"] = message
            context["unsubscribe_token"] = member.getUUID()
            message = inbox.utils.renderTemplate(template, context)
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        nr = NotificationMemberRecord(member=member, to_addr=member.email)
        email_record = NotificationRecord(
            method="email",
            subject=subject,
            from_addr=from_email,
            body=message)
        try:
            email_record.save()
            if attachments:
                email_record.addAttachments(attachments)
            email_record.send([nr])
        except Exception as err:
            rh.log_exception("email send failed", member.username, subject)

    @classmethod
    def notifyLegacy(cls, notify_users, subject, message=None, 
               template=None, context=None, email_only=False,
               sms_msg=None, force=False,
               from_email=settings.DEFAULT_FROM_EMAIL,
               attachments=[]):
        # this will create a record for each email address message is sent to
        from telephony.models import SMS
        email_to = []
        email_list = []
        sms_to = []

        if not message and not template and subject:
            message = subject
        if not sms_msg and subject:
            sms_msg = subject
        if not sms_msg and message:
            sms_msg = message

        if subject and len(subject) > 80:
            epos = subject.find('. ') + 1
            if epos > 10:
                subject = subject[:epos]
            else:
                subject = subject[:80]
                subject = subject[:subject.rfind(' ')] + "..."

        if template:
            # render message now so we can save message
            if context is None:
                context = {}
            if message is not None:
                context["body"] = message
            message = inbox.utils.renderTemplate(template, context)
            # message = rest_mail.renderBody(message, template, context)
            template = None
            context = None

        email_record = None
        for member in notify_users:
            via = member.getProperty("notify_via", "all")
            phone = member.getProperty("phone")
            email = member.email
            valid_email = email is not None and "@" in email and "invalid" not in email
            allow_sms = not email_only and phone and (force or via in ["all", "sms"])
            allow_email = not member.email_disabled and valid_email and (force or via in ["all", "email"])
            if not allow_email and not allow_sms:
                continue
            if allow_email and email not in email_list:
                email_list.append(email)
                nr = NotificationMemberRecord(member=member, to_addr=email)
                email_to.append(nr)
            if not email_only and allow_sms and phone not in sms_to:
                sms_to.append(phone)

        if sms_to:
            for phone in sms_to:
                SMS.send(phone, sms_msg)

        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        if email_to:
            # lets verify the db is working
            email_record = NotificationRecord(
                method="email",
                subject=subject,
                from_addr=from_email,
                body=message)
            try:
                email_record.save()
                email_record.addAttachments(attachments)
                email_record.send(email_to)
            except Exception as err:
                rh.log_exception("email send failed", email_to)
                # we need to send emails the old way
                addrs = []
                for to in email_to:
                    addrs.append(to.to_addr)
                rest_mail.send(
                    addrs,
                    subject,
                    message,
                    attachments=attachments,
                    do_async=True)


class NotificationAttachment(models.Model, RestModel):
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    notification = models.ForeignKey(NotificationRecord, related_name="attachments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    data = models.TextField()


class NotificationMemberRecord(models.Model, RestModel):
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    member = models.ForeignKey(
        "account.Member", related_name="notifications",
        default=None, null=True, on_delete=models.CASCADE)
    notification = models.ForeignKey(NotificationRecord, related_name="to", on_delete=models.CASCADE)
    to_addr = models.CharField(max_length=255, db_index=True)


class BounceHistory(models.Model, RestModel):
    class RestMeta:
        CAN_SAVE = False
        SEARCH_FIELDS = ["address"]
        SEARCH_TERMS = [("email", "address"), ("to", "address"), "source", "reason", "state", ("user", "user__username")]
        GRAPHS = {
            "default": {
                "graphs": {
                    "user": "basic"
                }
            },
            "list": {
                "graphs": {
                    "user": "basic"
                }
            }
        }
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    user = models.ForeignKey("account.Member", related_name="bounces", null=True, blank=True, default=None, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, db_index=True)
    kind = models.CharField(max_length=32, db_index=True)
    reason = models.TextField(null=True, blank=True, default=None)
    reporter = models.CharField(max_length=255, null=True, blank=True, default=None)
    code = models.CharField(max_length=32, null=True, blank=True, default=None)
    source = models.CharField(max_length=255, null=True, blank=True, default=None)
    source_ip = models.CharField(max_length=64, null=True, blank=True, default=None)

    @staticmethod
    def log(kind, address, reason, reporter=None, code=None, source=None, source_ip=None, user=None):
        obj = BounceHistory(kind=kind, address=address)
        obj.reason = reason
        obj.reporter = reporter
        obj.code = code
        obj.source = source
        obj.source_ip = source_ip
        if user is None:
            Member = RestModel.getModel("account", "Member")
            user = Member.objects.filter(email=address).last()
            # now lets check our bounced count, if more then 3, we turn off email
            if user:
                user.log("bounced", "{} bounced to {} from {}".format(kind, address, source_ip), method=kind)
                since = datetime.now() - timedelta(days=14)
                bounce_count = BounceHistory.objects.filter(user=user, created__gte=since).count()
                if bounce_count > 2:
                    # TODO notify support an account has been disabled because of bounce
                    user.setProperty("notify_via", "off")
                    user.addPermission("email_disabled")
                    user.log("disabled", "notifications disabled because email bounced", method="notify")
        else:
            # TODO notify support of unknown bounce
            pass
        obj.user = user
        obj.save()

