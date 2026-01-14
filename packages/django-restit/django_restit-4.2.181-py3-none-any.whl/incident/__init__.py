from objict import objict

META_KEYS = ["SERVER_PROTOCOL", "REQUEST_METHOD", "QUERY_STRING", "HTTP_USER_AGENT"]


def _request_to_meta(request, metadata):
    metadata.ip = request.ip
    if "path" not in metadata:
        metadata.path = request.path
    for key in META_KEYS:
        value = request.META.get(key, None)
        if value is not None and isinstance(value, str) and "." not in key:
            metadata[key.lower()] = str(value)
    if hasattr(request, "buid"):
        metadata["buid"] = request.buid
    if "username" not in metadata and hasattr(request, "member") and request.member is not None:
        metadata["username"] = request.member.username
    # if "group_name" not in metadata and hasattr(request, "group") and request.group is not None:
    #     metadata['group_name'] = request.group.name
    #     metadata['group_id'] = request.group.id
    return metadata


def event(category, description, level=10, request=None, group=None, **kwargs):
    from taskqueue.models import Task
    data = objict(category=category, description=description, level=level, group=group)
    data.metadata = objict.fromdict(kwargs)
    if request is not None:
        _request_to_meta(request, data.metadata)
    Task.Publish("incident", "new_event", channel="tq_app_handler", data=data)


def event_now(category, description, level=10, request=None, group=None, **kwargs):
    from .models.event import Event
    data = objict(category=category, description=description, level=level, group=group)
    data.metadata = objict.fromdict(kwargs)
    if request is not None:
        _request_to_meta(request, data.metadata)
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
    Event.createFromDict(None, data)


def exception_event(request, error, body=None, stack=None, 
                    title="REST Error", level=1,
                    category="rest_exception", **kwargs):
    from rest import settings
    import traceback
    if stack is None:
        stack = str(traceback.format_exc())
    host = request.get_host()
    server = settings.get("HOSTNAME", "unknown")
    if body is None:
        try:
            body = request.body.decode('utf-8')
        except Exception:
            body = request.DATA.asDict()
    description = kwargs.pop("description", error)
    subject = f"{title} on {host} : {error}"
    username = "anonymous"
    if request.member:
        username = request.member.username

    metadata = {
        "method": request.method,
        "path": request.path,
        "server": server,
        "error": str(error),
        "username": username,
        "ip": request.ip,
    }

    for k, v in kwargs.items():
        metadata[k] = v

    if request.auth_model is not None:
        metadata['auth_model'] = str(request.auth_model)
    if request.group is not None:
        metadata['group_name'] = request.group.name
        metadata['group_id'] = request.group.id
    if hasattr(request, "buid"):
        metadata["buid"] = request.buid
    if hasattr(request, "_log_component"):
        metadata["component"] = request._log_component
        metadata["pkey"] = request._log_pk

    event_now(
        category, description=subject, level=level, hostname=host,
        details=stack, reporter_ip=request.ip, request=request,
        **metadata)
