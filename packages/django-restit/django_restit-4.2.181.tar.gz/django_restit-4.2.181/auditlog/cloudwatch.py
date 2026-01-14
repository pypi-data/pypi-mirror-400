import boto3
from datetime import datetime, timedelta
import re
import time
import json
from objict import objict
from rest import settings
from rest import datem
from rest import helpers as rh
from concurrent.futures import ThreadPoolExecutor


LOG_CACHE = objict()


def getClient():
    if LOG_CACHE.client is None:
        key = settings.AWS_KEY
        secret = settings.AWS_SECRET
        region = settings.AWS_REGION
        LOG_CACHE.client = boto3.client("logs", aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)
    return LOG_CACHE.client


def log(data, log_group, log_stream):
    if LOG_CACHE.pool is None:
        LOG_CACHE.pool = ThreadPoolExecutor(max_workers=1)
    LOG_CACHE.pool.submit(logToCloudWatch, data, log_group, log_stream)
    return True


def get(log_group, log_stream, size=20):
    client = getClient()
    if log_stream is None:
        log_stream = DEFAULT_LOG_STREAMS
    if isinstance(log_stream, list):
        log_events = client.get_log_events(
            logGroupName=log_group,
            logStreamNames=log_stream,
            limit=size,
            startFromHead=False
        )
    else:
        log_events = client.get_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            limit=size,
            startFromHead=False
        )

    return log_events



def logToCloudWatch(message, log_group, log_stream):
    if isinstance(message, dict):
        message = json.dumps(message)
    return logBatchToCloudWatch([
            dict(
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                message=message)
        ], log_group, log_stream)


def logBatchToCloudWatch(batch, log_group, log_stream):
    return getClient().put_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        logEvents=batch
    )


def getLogGroups(names_only=True):
    response = getClient().describe_log_groups()
    groups = response.get('logGroups', [])
    if names_only:
        return [item["logGroupName"] for item in groups]
    return groups


def getLogStreams(log_group):
    log_streams = client.describe_log_streams(
        logGroupName=log_group_name
    )
    return log_streams['logStreams']


def createLogStream(log_group, log_stream):
    try:
        getClient().create_log_stream(logGroupName=log_group, logStreamName=log_stream)
    except Exception:
        pass  # Log stream already exists, no need to create it


def filter(log_group, log_streams, pattern, start_time="1h", end_time=None, resp_format=None):
    if log_streams is None:
        log_streams = DEFAULT_LOG_STREAMS

    start_time, end_time = datem.convert_to_epoch_range(start_time, end_time)
    rh.debug("filter", start_time, end_time, pattern, log_group, log_streams)
    client = getClient()
    response =client.filter_log_events(
        logGroupName=log_group,
        logStreamNames=log_streams,
        filterPattern=f'"{pattern}"',
        startTime=start_time,
        endTime=end_time,
        limit=1000
    )
    rh.debug("filter_log_events", response)
    out = []
    out.extend(response["events"])
    prev_next = None
    while "nextToken" in response and response["nextToken"]:
        if prev_next == response["nextToken"]:
            break
        prev_next = response["nextToken"] 
        response = client.filter_log_events(
            logGroupName=log_group,
            logStreamNames=log_streams,
            filterPattern=f'"{pattern}"',
            startTime=start_time,
            endTime=end_time,
            nextToken=response["nextToken"]
        )
        rh.debug("filter_log_events", response)
        out.extend(response["events"])
    if resp_format == "nginx":
        return dict(events=parseNginxEvents(out))
    return dict(events=out)


QUERY_BY_IP = """fields @message 
| filter @logStream in {log_streams}
| filter @message like /^{ip}/"""

QUERY_BY_TEXT = """fields @message 
| filter @logStream in {log_streams}
| filter @message like "{text}" """

DEFAULT_LOG_STREAMS = ["access.log", "ui_access.log"]

def startSearch(log_groups, start_time, end_time=None, 
                text=None, ip=None, query_string=None,
                log_streams=DEFAULT_LOG_STREAMS):
    if log_streams is None:
        log_streams = DEFAULT_LOG_STREAMS
    # 173\.196\.133\.90
    if ip is not None and "." in ip:
        query_string = QUERY_BY_IP.format(ip=ip.replace('.', '\.'), log_streams=log_streams)
    elif text is not None:
        query_string = QUERY_BY_TEXT.format(text=text, log_streams=log_streams)
    return startInsights(log_groups, start_time, end_time, query_string)


def startInsights(log_groups, start_time, end_time, query_string):
    """
    Executes a CloudWatch Logs Insights query and returns the results.

    :param log_group: The name of the log group to query.
    :param start_time: The start time of the query (epoch time in seconds).
    :param end_time: The end time of the query (epoch time in seconds).
    :param query_string: The query string to use.
    :param region_name: AWS region name.
    :return: The query results.
    """
    # Create a CloudWatch Logs client
    client = getClient()
    start_time, end_time = datem.convert_to_epoch_range(start_time, end_time)

    if log_groups is None:
        log_groups = getLogGroups()
    
    # Start the query
    start_query_response = client.start_query(
        logGroupNames=log_groups,
        startTime=start_time,
        endTime=end_time,
        queryString=query_string,
    )
    return dict(query_id=start_query_response['queryId'], query=query_string)
    

def getInsightResults(query_id, resp_format=None):
    # Wait for the query to complete
    resp = getClient().get_query_results(queryId=query_id)
    status = resp["status"].lower()
    results = insightsToMessage(resp["results"])
    stats = resp["statistics"]
    if status == "complete" and resp_format == "nginx":
        results = parseNginxEvents(results)
    return dict(status=True, state=status, stats=stats, data=results, count=len(results))


def insightsToMessage(events):
    out = []
    for fields in events:
        obj = {}
        for field in fields:
            if "field" in field and field["field"][0] == "@":
                obj[field["field"][1:]] = field["value"]
        if obj:
            out.append(obj)
    return out

def parseNginxEvents(events):
    pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<time>.+?)\] '
        r'"(?P<method>\w+) (?P<url>.+?) (?P<protocol>[\w/.]+)" '
        r'(?P<status>\d+) (?P<bytes>\d+) "(?P<referer>.+?)" '
        r'"(?P<user_agent>.+?)" (?P<request_time>\S+) (?P<server_port>\d+)'
    )
    return [pattern.match(line["message"]).groupdict() for line in events]
