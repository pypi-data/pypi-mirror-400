from rest import settings
from rest import ssl_check
from datetime import datetime, timedelta
import incident


def run_monitoring(task):
    checkDomains(task)


def checkDomains(task):
    if not settings.DOMAIN_WATCH:
        task.log("no domains to check")
        return False
    now = datetime.utcnow()
    alarm_date = now + timedelta(days=30)
    result = ssl_check.check(*settings.DOMAIN_WATCH)
    for key, value in result.items():
        if value is None or isinstance(value, str):
            continue
        if value < alarm_date:
            task.log(f"{key} is expiring soon")
            notifyDomainExpiring(key, value)


def notifyDomainExpiring(domain, expires):
    incident.event_now(
        "domain_expires",
        f"{domain} is expiring",
        level=1, hostname=domain,
        domain=domain)
