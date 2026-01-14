from rest import settings
from rest.log import getLogger
from objict import objict
import metrics
import boto3
import threading
from . import render as mr

EMAIL_LOGGER = getLogger("email", filename="email.log")
# ses settings
SES_ACCESS_KEY = settings.SES_ACCESS_KEY
SES_SECRET_KEY = settings.SES_SECRET_KEY
SES_REGION = settings.SES_REGION
EMAIL_METRICS = settings.EMAIL_METRICS
EMAIL_ASYNC_AS_TASK = settings.EMAIL_ASYNC_AS_TASK

# write python regect to detect if text is html


def send(sender, recipients, subject, message, attachments=None, replyto=None, fail_silently=False, do_async=False):
    html = None
    text = None
    if mr.isHTML(message):
        # assume html?
        html = message
    else:
        text = message
    msg = mr.createMessage(sender, recipients, subject, text, html, attachments=attachments, replyto=replyto)
    # METRICS FAIL WHEN SWITCHING THREADS
    # if do_async:
    #     t = threading.Thread(target=sendMail, args=[msg.msg, msg.sender, msg.recipients])
    #     t.start()
    #     return True
    return sendMail(msg.msg, msg.sender, msg.recipients, fail_silently=fail_silently)


def sendMail(msg, sender, recipients, fail_silently=True):
    return sendMailViaSES(msg, sender, recipients, fail_silently)


def sendMailViaSES(msg, sender, recipients, fail_silently=True):
    try:
        ses_client = getSES(SES_ACCESS_KEY, SES_SECRET_KEY, SES_REGION)
        ses_client.send_raw_email(
            Source=sender,
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )
        if EMAIL_METRICS:
            metrics.metric("emails_sent", category="email", min_granularity="hourly")
        return True
    except Exception as err:
        if EMAIL_METRICS:
            metrics.metric("email_errors", category="email", min_granularity="hourly")
        EMAIL_LOGGER.exception(err)
        EMAIL_LOGGER.error(msg.as_string())
        if not fail_silently:
            raise err
    return False


def getSES(access_key, secret_key, region):
    return boto3.client(
        'ses',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
