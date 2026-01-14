from objict import objict
from datetime import datetime
import re
from .. import models as am
from location.models import GeoIP

IGNORE_RULES = [
    "100020"
]

LEVEL_REMAP_BY_RULE = {
    5402: 7,
    5710: 5
}

NGINX_PARSE_PATTERN = re.compile(
    r'(?P<src_ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<http_time>.+?)\] '
    r'(?P<http_method>\w+) (?P<http_url>.+?) (?P<http_protocol>[\w/.]+) '
    r'(?P<http_status>\d+) (?P<http_bytes>\d+) (?P<http_referer>.+?) '
    r'(?P<user_agent>.+?) (?P<http_elapsed>\d\.\d{3})'
)

def parse_nginx_line(line):
    if "\n" in line:
        for l in line.split('\n'):
            match = NGINX_PARSE_PATTERN.match(l)
            if match:
                return match.groupdict()
        return None
    match = NGINX_PARSE_PATTERN.match(line)
    if match:
        return match.groupdict()
    return None


def removeNonAscii(input_str, replacement=''):
    """
    Replace all non-ASCII characters and escaped byte sequences in the input string with a specified string.
    
    Args:
    input_str (str): The string to process.
    replacement (str): The string to use as a replacement for non-ASCII characters and escaped byte sequences.

    Returns:
    str: The processed string with non-ASCII characters and byte sequences replaced.
    """
    # Replace escaped byte sequences with the replacement string
    cleaned_str = re.sub(r'\\x[0-9a-fA-F]{2}', replacement, input_str)
    # Replace non-ASCII characters with the replacement string
    return ''.join(char if (32 <= ord(char) < 128 or char in '\n\r\t') else f"<r{str(ord(char))}>" for char in cleaned_str)


def extractURL(text):
    match = re.search(r"(GET|POST|DELETE|PUT)\s+(https?://[^\s]+)\s+HTTP/\d\.\d", text)
    if match:
        return match.group(2)
    return None


def extractDomain(text):
    match = re.search(r"https?://([^/:]+)", text)
    if match:
        return match.group(1)
    return None


def extractIP(text):
    match = re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)
    if match:
        return match.group(1)
    return None


def extractUrlPath(text):
    match = re.search(r"https?://[^/]+(/[^?]*)", text)
    if match:
        return match.group(1)
    return None


def extractUserAgent(text):
    # this only works if the referrer is '-'
    match = re.search(r"' - (.+?) \d+\.\d+ \d+'", text)
    if match:
        return match.group(1)
    return None


def extractMetaData(alert):
    return parse_alert_metadata(alert)


DEFAULT_META_PATTERNS = {
    "src_ip": re.compile(r"Src IP: (\S+)"),
    "src_port": re.compile(r"Src Port: (\S+)"),
    "user": re.compile(r"User: (\S+)"),
    "path": re.compile(r"request: (\S+ \S+)"),
    "http_server": re.compile(r"server: (\S+),"),
    "http_host": re.compile(r"host: (\S+)"),
    "http_referrer": re.compile(r"referrer: (\S+),"),
    "client": re.compile(r"client: (\S+),"),
    "upstream": re.compile(r"upstream: (\S+),")
}


def parse_alert_metadata(alert):
    patterns = DEFAULT_META_PATTERNS
    if alert.rule_id == "2501":
        match = re.search(r'user (\w+) (\d+\.\d+\.\d+\.\d+) port (\d+)', alert.text)
        if match:
            return dict(username=match.group(1), src_ip=match.group(2), src_port=match.group(3))
    elif alert.rule_id.startswith("311") or alert.rule_id in ["31516", "31508", "31516"]:
        data = parse_nginx_line(alert.text)
        if data:
            return data
    elif alert.rule_id in ["31301"]:
        match = re.search(r'\((?P<error_code>\d+): (?P<error_message>.*?)\)', alert.text)
        data = match_patterns(patterns, alert.text)
        data["action"] = "error"
        if match:
            data.update(match.groupdict())
        return data
    elif alert.rule_id in ["31302", "31303"]:
        match = re.search(r'\[(warn|crit|error)\].*?: (.*?),', alert.text)
        data = match_patterns(patterns, alert.text)
        
        if match:
            data["action"] = match.group(1)
            emsg = match.group(2)
            if emsg[0] == "*":
                emsg = emsg[emsg.find(' ')+1:]
            data["error_message"] = emsg
        return data
    elif alert.rule_id == "551":
        match = re.search(r"Integrity checksum changed for: '(\S+)'", alert.text)
        if match:
            return dict(filename=match.group(1), action="changed")
    elif alert.rule_id == "554":
        match = re.search(r"New file '(\S+)' added", alert.text)
        if match:
            return dict(filename=match.group(1), action="added")
    elif alert.rule_id == "5402":
        match = re.search(r'(?P<username>[\w-]+) : PWD=(?P<pwd>\S+) ; USER=(?P<user>\w+) ; COMMAND=(?P<command>.+)', alert.text)
        if match:
            return match.groupdict()
        match = re.search(r'(?P<username>[\w-]+) : TTY=(?P<tty>\S+) ; PWD=(?P<pwd>\S+) ; USER=(?P<user>\w+) ; COMMAND=(?P<command>.+)', alert.text)
        if match:
            return match.groupdict()
    elif alert.rule_id in ["5501", "5502"]:
        match = re.search(r"session (?P<action>\S+) for user (?P<username>\S+)*", alert.text)
        if match:
            return match.groupdict()
    elif alert.rule_id in ["5704", "5705"]:
        match = re.search(r"(?P<src_ip>\d{1,3}(?:\.\d{1,3}){3}) port (?P<src_port>\d+)", alert.text)
        if match:
            return match.groupdict()
    elif alert.rule_id == "5715":
        match = re.search(r'Accepted publickey for (?P<username>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) .*: (?P<ssh_key_type>\S+) (?P<ssh_signature>\S+)', alert.text)
        if match:
            return match.groupdict()
    elif alert.rule_id == "2932":
        match = re.search(r"Installed: (\S+)", alert.text)
        if match:
            return dict(package=match.group(1))
    return match_patterns(patterns, alert.text)


def match_patterns(patterns, text):
    # Search for matches in the text
    return {key: pattern.search(text).group(1) for key, pattern in patterns.items() if pattern.search(text)}


def parse_alert_json(data):
    try:
        if isinstance(data, str):
            data = objict.fromJSON(removeNonAscii(data.replace('\n', '\\n')))
    except Exception:
        data = objict.fromJSON(removeNonAscii(data))
    for key in data:
        data[key] = data[key].strip()
    if data.text:
        data.text = removeNonAscii(data.text)
    return data


def ignore_alert(alert):
    if alert.rule_id in IGNORE_RULES:
        return True
    if alert.rule_id == "510" and "/dev/.mount/utab" in alert.text:
        return True
    return False


def parse_alert_id(details):
    match = re.search(r"Alert (\d+\.\d+):", details)
    if match:
        return match.group(1)
    return ""


def parse_rule_details(details):
    alert_id = parse_alert_id(details)
    rule_pattern = r"Rule: (\d+) \(level (\d+)\) -> '([^']+)'"
    match = re.search(rule_pattern, details)
    if match:
        return objict(
            rid=int(match.group(1)), level=int(match.group(2)), 
            title=match.group(3), alert_id=alert_id)
    return objict(alert_id=alert_id)


def parse_when(alert):
    return datetime.utcfromtimestamp(int(alert.alert_id[:alert.alert_id.find(".")]))


def truncate_str(text, length):
    if len(text) > length:
        text = text[:length]
        text = text[:text.rfind(' ')] + "..."
    return text


def update_by_rule(data, geoip=None):
    if data.rule_id == "2501":
        data.title = f"SSH Auth Attempt {data.username}@{data.hostname} from {data.src_ip}"
    elif data.rule_id == "2503" and data.src_ip:
        data.title = f"SSH Auth Blocked from {data.src_ip}"
    elif data.rule_id == "31101" and data.http_status:
        data.title = f"Web {data.http_status} {data.http_method} {data.http_url} from {data.src_ip}"
    elif data.rule_id == "31104" and data.http_status:
        data.title = f"Web Attack {data.http_status} {data.http_method} {data.http_url} from {data.src_ip}"
    elif data.rule_id == "31111" and data.http_status:
        if geoip and geoip.isp:
            data.title = f"No referrer for .js - {data.http_status} {data.http_method} {data.http_url} from {data.src_ip}({geoip.isp})"
        else:
            data.title = f"No referrer for .js - {data.http_status} {data.http_method} {data.http_url} from {data.src_ip}"
    elif data.rule_id in ["31151", "31152", "31153"] and data.http_status:
        url = truncate_str(data.http_url, 50)
        data.title = f"Suspected Web Scan {url} from {data.src_ip}"
    elif data.rule_id == "31120" and data.http_status:
        url = truncate_str(data.http_url, 50)
        data.title = f"Web Error {data.http_status} {data.http_method} {url} from {data.src_ip}"
    elif data.rule_id.startswith("311") and data.http_status:
        url = truncate_str(data.http_url, 50)
        data.title = f"Web {data.http_status} {data.http_method} {url} from {data.src_ip}"
    elif data.rule_id in ["31301", "31302", "31303"] and data.error_message:
        if data.upstream and "ws/events" in data.upstream:
            data.title = f"Websocket Error: {data.error_message} on {data.hostname}"
        else:
            emsg = truncate_str(data.error_message, 50)
            data.title = f"Nginx {data.action}: {emsg} from {data.src_ip}"
    elif data.rule_id == "31516" and data.http_url:
        url = truncate_str(data.http_url, 50)
        data.title = f"Web Suspicious {data.http_status} {data.http_method} {url} from {data.src_ip}"
    elif data.rule_id == "533":
        data.title = f"Network Open Port Change Detected on {data.hostname}"
    elif data.rule_id == "5402":
        cmd = truncate_str(data.command, 50)
        data.title = f"Sudo(user: {data.user}) executed '{cmd}' on {data.hostname}"
    elif data.rule_id in ["551", "554"] and data.filename:
        name = truncate_str(data.filename, 50)
        data.title = f"File {data.action.capitalize()} on {data.hostname}: {name}"
    elif data.rule_id in ["5501", "5502"]:
        if "sudo" in data.text:
            data.title = f"Server Login {data.action} via sudo on {data.hostname}"
        else:
            data.title = f"Server Login {data.action} on {data.hostname}"
    elif data.rule_id == "5715":
        data.title = f"SSH Login Detected: {data.username}@{data.hostname} from {data.src_ip}"
    elif data.rule_id == "2932" and data.package:
        package = truncate_str(data.package, 60)
        data.title = f"Package Installed on {data.hostname}: {package}"
    elif data.src_ip and data.src_ip not in data.title:
        data.title = f"{data.title} Source IP: {data.src_ip}"
    if len(data.title) > 199:
        data.title = data.title[:199]

def parse_incoming_alert(data):
    alert = parse_alert_json(data)
    if ignore_alert(alert):
        return None
    alert.update(parse_rule_details(alert.text))
    if alert.title is None:
        return None
    alert.update(parse_alert_metadata(alert))
    if alert.src_ip in ["-", None] and alert.client:
        alert.src_ip = alert.client
    if alert.ext_ip in ["-", None]:
        alert.ext_ip = alert.src_ip
    update_by_rule(alert)
    return alert


def parseAlert(request, data):
    pdata = parse_incoming_alert(data)
    if pdata is None:
        return None
    field_names = am.ServerOssecAlert.get_model_field_names()
    soa = am.ServerOssecAlert(**{key:value for key, value in pdata.items() if key in field_names})
    soa.when = parse_when(pdata)
    soa.metadata = pdata
    if soa.src_ip is not None and len(soa.src_ip) > 6 and soa.src_ip != "127.0.0.1":
        soa.geoip = GeoIP.lookup(soa.src_ip)
        update_by_rule(pdata, soa.geoip)
        soa.title = pdata.title
    soa.save()
    return soa



