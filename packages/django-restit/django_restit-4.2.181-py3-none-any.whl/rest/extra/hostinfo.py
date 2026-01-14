from datetime import datetime
import time
from rest import helpers
from django.conf import settings
import django
import version
import platform
import socket
import subprocess


try:
    import psutil
except Exception:
    print("no psutil")

SOFTWARE_VERSIONS = getattr(settings, 'SOFTWARE_VERSIONS', None)


def getHostIP():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def getTcpEstablishedCount():
    return len(getTcpEstablished())


def getTcpEstablished(filter=None):
    cons = psutil.net_connections(kind="tcp")
    established = []
    for c in cons:
        if c.status == "ESTABLISHED":
            established.append(c)
    return filterConnections(established, filter)


def filterConnections(cons, filter):
    if filter == "https":
        return [c for c in cons if c.laddr.port == 443]
    elif filter == "redis":
        return [c for c in cons if c.raddr.port == 6379]
    elif filter == "postgres":
        return [c for c in cons if c.raddr.port == 5432]
    elif filter == "unknown":
        return [c for c in cons if c.raddr.port not in [5432, 6379] and c.laddr.port != 443]
    elif filter and ":" in filter:
        addr, port = filter.split(':')
        if addr == "raddr":
            return [c for c in cons if c.raddr.port == port]
        elif addr == "laddr":
            return [c for c in cons if c.laddr.port == port]
    return cons


def consToDict(cons):
    out = []
    cid = 0
    for c in cons:
        cid += 1
        out.append({
            "id": cid,
            "type": c.type.name,
            "status": c.status,
            "family": c.family.name,
            "raddr": {
                "port": c.raddr.port,
                "ip": c.raddr.ip
            },
            "laddr": {
                "port": c.laddr.port,
                "ip": c.laddr.ip
            }
        })
    return out


def getVersions(out=None):
    if out is None:
        out = {}
    for key in SOFTWARE_VERSIONS:
        if key == "django":
            out[key] = django.__version__
        else:
            out[key] = safe_cmd(SOFTWARE_VERSIONS[key])
    return out


def getHostInfo(include_versions=False, include_blocked=False):
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()

    out = {
        "time": time.time(),
        "datetime": str(datetime.now()),
        "version": version.VERSION,
        "os": {
            "system": platform.system(),
            "version": platform.version(),
            "hostname": platform.node(),
            "release": platform.release(),
            "processor": platform.processor(),
            "machine": platform.machine()
        },
        "boot_time": psutil.boot_time(),
        "cpu_load": psutil.cpu_percent(),
        "cpus_load": psutil.cpu_percent(percpu=True),
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }, 
        "users": psutil.users()
    }

    try:
        out["cpu"] = {
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq(),
        }
    except Exception:
        pass

    try:
        out["network"] = {
            "tcp_cons": getTcpEstablishedCount(),
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout,
            "dropin": net.dropin,
            "dropout": net.dropout
        }
    except Exception:
        pass

    if include_versions and SOFTWARE_VERSIONS:
        out["versions"] = getVersions()
    if include_blocked:
        out["blocked"] = helpers.getBlockedHosts()
    return out


def safe_cmd(cmd, *args):
    try:
        cmd_args = [cmd]
        if len(args):
            cmd_args.extend(list(args))
        return helpers.toString(subprocess.check_output(cmd_args, shell=True).strip())
    except Exception as err:
        return str(err)
        # print( str(err))
    return None
