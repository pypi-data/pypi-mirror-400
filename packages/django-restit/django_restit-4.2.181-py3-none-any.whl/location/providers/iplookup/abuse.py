import requests
import ipaddress
from objict import objict
from rest import settings
from datetime import datetime
from enum import Enum

API_KEY = settings.get("ABUSEIPDB_KEY", "")

DEFAULT_HEADERS = {
    'Accept': 'application/json',
    'Key': API_KEY
}


class AbuseCategory(Enum):
    DNS_COMPROMISE = (1, "Altering DNS records resulting in improper redirection.")
    DNS_POISONING = (2, "Falsifying domain server cache (cache poisoning).")
    FRAUD_ORDERS = (3, "Fraudulent orders.")
    DDOS_ATTACK = (4, "Participating in distributed denial-of-service (usually part of botnet).")
    FTP_BRUTE_FORCE = (5, "FTP Brute-Force")
    PING_OF_DEATH = (6, "Oversized IP packet.")
    PHISHING = (7, "Phishing websites and/or email.")
    FRAUD_VOIP = (8, "Fraud VoIP")
    OPEN_PROXY = (9, "Open proxy, open relay, or Tor exit node.")
    WEB_SPAM = (10, "Comment/forum spam, HTTP referer spam, or other CMS spam.")
    EMAIL_SPAM = (11, "Spam email content, infected attachments, and phishing emails.")
    BLOG_SPAM = (12, "CMS blog comment spam.")
    VPN_IP = (13, "Conjunctive category.")
    PORT_SCAN = (14, "Scanning for open ports and vulnerable services.")
    HACKING = (15, "Hacking")
    SQL_INJECTION = (16, "Attempts at SQL injection.")
    SPOOFING = (17, "Email sender spoofing.")
    BRUTE_FORCE = (18, "Credential brute-force attacks on webpage logins and services.")
    BAD_WEB_BOT = (19, "Webpage scraping and crawlers that do not honor robots.txt.")
    EXPLOITED_HOST = (20, "Host is likely infected with malware and being used for other attacks.")
    WEB_APP_ATTACK = (21, "Attempts to probe for or exploit installed web applications.")
    SSH = (22, "Secure Shell (SSH) abuse.")
    IOT_TARGETED = (23, "Abuse targeted at an 'Internet of Things' type device.")

    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return f"{self.name} ({self.code}): {self.description}"


def lookup(ip, max_days=0):
    """
    {
      "data": {
        "ipAddress": "118.25.6.39",
        "isPublic": true,
        "ipVersion": 4,
        "isWhitelisted": false,
        "abuseConfidenceScore": 100,
        "countryCode": "CN",
        "countryName": "China",
        "usageType": "Data Center/Web Hosting/Transit",
        "isp": "Tencent Cloud Computing (Beijing) Co. Ltd",
        "domain": "tencent.com",
        "hostnames": [],
        "isTor": false,
        "totalReports": 1,
        "numDistinctUsers": 1,
        "lastReportedAt": "2018-12-20T20:55:14+00:00",
        "reports": [
          {
            "reportedAt": "2018-12-20T20:55:14+00:00",
            "comment": "Dec 20 20:55:14 srv206 sshd[13937]: Invalid user oracle from 118.25.6.39",
            "categories": [
              18,
              22
            ],
            "reporterId": 1,
            "reporterCountryCode": "US",
            "reporterCountryName": "United States"
          }
        ]
      }
    }
    """
    if not API_KEY:
        return objict(errors=[{"detail": "Missing API KEY", "status": 401}])
    url = 'https://api.abuseipdb.com/api/v2/check'
    params = dict(ipAddress=ip)
    if max_days:
        params["maxAgeInDays"] = max_days
    response = requests.request(
        method='GET', url=url, headers=DEFAULT_HEADERS,
        params=params)
    output = objict.fromJSON(response.text)
    if "data" in output:
        return output.data
    return output


def reportAbuse(ip, comment, categories):
    """
    {
        "data": {
            "ipAddress": "127.0.0.1",
            "abuseConfidenceScore": 52
        }
    }
    """
    if not API_KEY:
        return objict(errors=[{"detail": "Missing API KEY", "status": 401}])
    url = 'https://api.abuseipdb.com/api/v2/report'
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params = dict(ip=ip, comment=comment, timestamp=now_str, categories=categories)
    response = requests.request(
        method='POST', url=url,
        headers=DEFAULT_HEADERS, params=params)
    return objict.fromJSON(response.text)


def isPrivate(ip, ignore_errors=False):
    if not ignore_errors:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except Exception:
        pass
    return None
