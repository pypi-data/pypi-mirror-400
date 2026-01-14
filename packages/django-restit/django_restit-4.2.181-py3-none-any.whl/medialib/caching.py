import io
from rest import settings
from medialib.stores import s3
from django.http import HttpResponse, StreamingHttpResponse
from datetime import datetime
AWS_CACHING_BUCKET = settings.get("AWS_CACHING_BUCKET", settings.AWS_S3_BUCKET)


def on_cached_rest_list(Model, request):
    cache_guid = request.DATA.get("format_filename")
    file_format = request.DATA.get("format", None)
    if not file_format:
        file_format = "csv"
        request.DATA.set("format", file_format)
    content_type = "text/csv"
    if file_format[:3] == "csv":
        file_format = "csv"
    else:
        file_format = "json"
        content_type = "application/json"
    if cache_guid:
        resp = getCachedResponse(cache_guid)
        if resp is not None:
            return resp
        resp = Model.on_rest_list(request)
        # TODO only cache if dr_end exists and is less then today
        dr_end = request.DATA.get("dr_end", field_type=datetime)
        if dr_end < datetime.now():
            cacheResponse(resp, cache_guid, content_type=content_type)
        return resp
    return Model.on_rest_list(request)


def getCachedResponse(cache_guid, content_type="application/json"):
    item = getCachedItem(cache_guid, content_type)
    if not item.exists:
        return None
    return _createResponse(item, cache_guid)


def getCachedItem(cache_guid, content_type="application/json"):
    url = f"s3://{settings.AWS_S3_BUCKET}/caching/{cache_guid}"
    return s3.S3Item(url, content_type)


def cacheResponse(response, cache_guid, content_type="application/json"):
    url = f"s3://{settings.AWS_S3_BUCKET}/caching/{cache_guid}"
    item = s3.S3Item(url, content_type)
    if isinstance(response, StreamingHttpResponse):
        # Access the streaming content and convert it to a file-like object
        content = io.BytesIO()
        for chunk in response.streaming_content:
            content.write(chunk)
        # Reset the file pointer to the beginning before uploading
        content.seek(0)
        item.upload(content)
        content.seek(0)
        response.streaming_content = iter(lambda: content.read(8192), b'')
    else:
        item.upload(response.content)
    return item


def _createResponse(item, cache_guid):
    # Create a StreamingHttpResponse object with the file iterator
    fp = item.download()
    fp.seek(0)
    fp.name = cache_guid
    response = StreamingHttpResponse(fp)
    # Add the appropriate content type header to the response
    # You might want to dynamically determine the content type based on the file
    response['Content-Type'] = item.content_type
    # Set the Content-Disposition header to prompt download with a filename
    response['Content-Disposition'] = f'attachment; filename="{cache_guid}"'
    return response
