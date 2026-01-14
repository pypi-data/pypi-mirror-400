from django.template.loader import render_to_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from rest import settings
import os
from objict import objict
from inbox.models.template import MailTemplate
import csv
from io import StringIO
import re


def createMessage(sender, recipients, subject, text, html, attachments=None, replyto=None):

    if isinstance(recipients, str):
        if "," in recipients:
            recipients = [t.strip() for t in recipients.split(',')]
        elif ";" in recipients:
            recipients = [t.strip() for t in recipients.split(';')]

    if not isinstance(recipients, (tuple, list)):
        recipients = [recipients]

    message = objict(sender=sender, recipients=recipients)

    if attachments is None:
        attachments = []

    message.msg = createMultiPartMessage(
        message.sender, message.recipients, subject,
        text=text, html=html, attachments=attachments,
        replyto=replyto)
    return message


def createMultiPartMessage(sender, recipients, subject, text, html, attachments, replyto):
    """
    Creates a MIME multipart message object.
    Uses only the Python `email` standard library.
    Emails, both sender and recipients, can be just the email string or have the format 'The Name <the_email@host.com>'.

    :param sender: The sender.
    :param recipients: List of recipients. Needs to be a list, even if only one recipient.
    :param subject: The subject of the email.
    :param text: The text version of the email body (optional).
    :param html: The html version of the email body (optional).
    :param attachments: List of files to attach in the email.
    :param replyto: optional reply to address.
    :return: A `MIMEMultipart` to be used to send the email.
    """
    multipart_content_subtype = 'alternative' if text and html else 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    if replyto:
        msg.add_header('reply-to', replyto)

    # Record the MIME types of both parts - text/plain and text/html.
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
    if text:
        part = MIMEText(text, 'plain')
        msg.attach(part)
    if html:
        # HACK to remove codec errors
        html = html.encode('ascii', 'ignore').decode('ascii')
        part = MIMEText(html, 'html')
        msg.attach(part)

    # Add attachments
    index = 0
    for atch in attachments or []:
        if isinstance(atch, (str, bytes)):
            index += 1
            atch = objict(name="attachment{}.txt".format(index), data=atch, mimetype="text/plain")
        # lets attach it
        part = MIMEApplication(atch.data)
        part.add_header('Content-Type', atch.mimetype)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(atch.name))
        msg.attach(part)
    return msg


def renderTemplate(template, context, group=None):
    context["SITE_LABEL"] = settings.SITE_LABEL
    context["BASE_URL"] = settings.BASE_URL
    context["SITE_LOGO"] = settings.SITE_LOGO
    context["SERVER_NAME"] = settings.SERVER_NAME
    context["UNSUBSCRIBE_URL"] = settings.get("UNSUBSCRIBE_URL", f"{settings.BASE_URL}/api/account/unsubscribe")
    context["version"] = settings.VERSION
    if "COMPANY_NAME" not in context and settings.COMPANY_NAME:
        context["COMPANY_NAME"] = settings.COMPANY_NAME

    if template[-4:] in ["html", ".txt"]:
        # this is a django template
        return render_to_string(template, context)
    qset = MailTemplate.objects.filter(name=template)
    if group is not None:
        gqset = qset.filter(group=group)
        mtemp = gqset.last()
        if mtemp is None:
            mtemp = qset.last()
    else:
        mtemp = qset.last()
    if mtemp is None:
        return None
    return mtemp.render(context)


def generateCSV(qset, fields, name):
    a = objict()
    a.name = name
    a.file = StringIO.StringIO()
    csvwriter = csv.writer(a.file)
    csvwriter.writerow(fields)

    for row in qset.values_list(*fields):
        row = [str(x) for x in row]
        csvwriter.writerow(row)
    a.data = a.file.getvalue()
    a.mimetype = "text/csv"
    return a


def isHTML(text):
    pattern = r'<[a-zA-Z0-9]+>.*?<\/[a-zA-Z0-9]+>'
    if re.search(pattern, text):
        return True
    return False
