from io import StringIO
import email
import re

from email.utils import parseaddr, parsedate_to_datetime, getaddresses
from email.header import decode_header

from objict import objict


def parseRawMessage(msgobj):
    """
    Parse the email and return a dictionary of relevant data.
    """
    if isinstance(msgobj, str):
        msgobj = email.message_from_string(msgobj)

    subject = None
    message = None
    body = None
    html = None
    attachments = []
    body_parts = []
    html_parts = []

    if msgobj['Subject'] is not None:
        decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s, enc in decodefrag:
            if enc:
                s = str(s, enc).encode('utf8', 'replace')
            subj_fragments.append(s)
        subject = ''.join(subj_fragments)

    for part in msgobj.walk():
        attachment = parseAttachment(part)
        if attachment is None:
            continue
        if attachment.content:
            if attachment.content_type == "text/html":
                html_parts.append(attachment.content)
            elif attachment.content_type == "text/plain":
                body_parts.append(attachment.content)
        else:
            attachments.append(attachment)

    if len(body_parts):
        message = []
        body = "".join(body_parts)
        body = body.strip()
        # now lets parse the first part of the message that is not "quoted"
        blocks = 0
        for line in body.split('\n'):
            if line.startswith('>'):
                blocks += 1
                if blocks > 3:
                    break
                continue
            blocks = 0
            message.append(line.strip())
        message = "\n".join(message).strip()

    if len(html_parts):
        html = "".join(html_parts)

    from_addr = parseaddr(msgobj.get('From'))
    date_time = parsedate_to_datetime(msgobj.get('Date')).replace(tzinfo=None)
    return objict({
        'subject': subject.strip(),
        'body': body,
        'sent_at': date_time,
        'message': message,
        'html': html,
        'from_email': from_addr[1],
        'from_name': from_addr[0],
        'to': msgobj.get("To"),
        'to_addrs': getaddresses(msgobj.get_all("To", [])),
        'cc': msgobj.get("Cc"),
        'cc_addrs': getaddresses(msgobj.get_all("Cc", [])),
        'attachments': attachments,
    })


def decodePayload(part):
    return str(part.get_payload(decode=True), part.get_content_charset(), 'replace')


def parseAttachment(message_part):
    content_disposition = message_part.get("Content-Disposition", None)
    content_type = message_part.get_content_type()
    if content_disposition is None and content_type == "multipart/alternative":
        return None
    attachment = objict()
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        attachment.dispositions = dispositions
        attachment.disposition = dispositions[0]
    attachment.payload = message_part.get_payload(decode=False)
    attachment.charset = message_part.get_content_charset()
    attachment.content_type = message_part.get_content_type()
    attachment.encoding = message_part.get("Content-Transfer-Encoding", "utf8")
    if attachment.disposition in [None, "inline"] and attachment.content_type in ["text/plain", "text/html"]:
        attachment.content = decodePayload(message_part)
    attachment.name = None
    attachment.create_date = None
    attachment.mod_date = None
    attachment.read_date = None

    if content_disposition:
        # print dispositions
        for param in dispositions[1:]:
            name, value = param.split("=")
            name = name.strip().lower()
            if name == "filename":
                if value.startswith('"') or value.startswith("'"):
                    value = value.strip()[1:-1]
                attachment.name = value
            elif name in ["create-date", "creation-date"]:
                attachment.create_date = value
            elif name == "modification-date":
                attachment.mod_date = value
            elif name == "read-date":
                attachment.read_date = value
    return attachment


def toFileObject(attachment):
    obj = StringIO(toString(attachment.payload))
    obj.name = attachment.name
    obj.size = len(attachment.payload)
    return obj


def parseAddresses(input_string, force_name=False, emails_only=False):
    if input_string is None:
        return []
    # Define a regex pattern to capture email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    # Find all matches of the pattern in the input string
    emails = re.findall(email_pattern, input_string)
    # Create a list to hold parsed email data
    parsed_emails = []
    for addr in emails:
        # Extract name if it exists
        name_match = re.search(r'([a-zA-Z\s]+)?\s*<{}>'.format(re.escape(addr)), input_string)
        addr = addr.strip().lower()
        full_email = addr
        if name_match and name_match.group(1):
            name = name_match.group(1).strip()
            full_email = f"{name} <{addr}>"
        elif force_name:
            name = addr.split('@')[1]
        else:
            name = None
        parsed_emails.append(objict(name=name, email=addr, full_email=full_email))
    if emails_only:
        return [email.email for email in parsed_emails]
    return parsed_emails


def toString(value):
    if isinstance(value, bytes):
        value = value.decode()
    elif isinstance(value, bytearray):
        value = value.decode("utf-8")
    elif isinstance(value, (int, float)):
        value = str(value)
    return value
