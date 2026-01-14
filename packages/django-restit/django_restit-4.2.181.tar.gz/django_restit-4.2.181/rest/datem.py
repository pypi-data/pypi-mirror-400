"""
It is critical to store everything in UTC.
Timezone that have DST (Daylight Savings)
or repeat an hour once a year.

When calculating actual elapsed time if using timezone aware objects
convert to epoch or use

"""


from dateutil.parser import parse as date_parser
from datetime import date, datetime, timedelta
import calendar
import pytz
import time
import re


def tz_datetime(timezone_str, year=2023, month=1, day=1, hour=0, minute=0, second=0):
    timezone = pytz.timezone(timezone_str)
    return datetime(
        year=year, month=month, day=day, 
        hour=hour, minute=minute, second=second,
        tzinfo=timezone)


def delta_seconds(d1, d2):
    if isinstance(d1, (int, float)):
        return d1 - d2
    if d1.tzinfo is not None or d2.tzinfo is not None:
        if d1.tzinfo is None:
            d1 = d2.tzinfo.localize(d1)
        elif d2.tzinfo is None:
            d2 = d1.tzinfo.localize(d2)
    return (d1 - d2).total_seconds()


def delta_hours(start, end):
    return int(delta_seconds(start, end) / 60 / 60)


def delta_days(start, end):
    return int(delta_seconds(start, end) / 60 / 60 / 24)


def epoch_offset(epoch_time, minutes=None, hours=None, days=None, timezone_str='UTC'):
    # Convert epoch time to timezone-aware datetime
    dt = datetime.fromtimestamp(epoch_time)
    # Calculate the same time on the previous day
    new_dt = offsetDate(dt, minutes=minutes, hours=hours, days=days)
    return new_dt.timestamp()


def offsetDate(when=None, minutes=None, hours=None, days=None):
    """
    Generates a new datetime object based on the offesets provides
    offsets can be negative or positive
    """
    params = {}
    if minutes is not None:
        params["minutes"] = minutes
    if hours is not None:
        params["hours"] = hours
    if days is not None:
        params["days"] = days
    if when is None:
        when = datetime.now()
    return when + timedelta(**params)


def convertToEpoch(dt):
    return time.mktime(dt.timetuple())


def getShortTZ(zone, when=None):
    timezone = pytz.timezone(zone)
    if not when:
        when = datetime.today()
    ltz = timezone.localize(when, is_dst=None)
    return ltz.tzname()


def convertToLocalTime(zone, when=None, tz_aware=False):
    """
    convert timezones in python can result in minutes shifting...
    just do a simple hour offset with timedelta
    """
    if when is None:
        when = datetime.today()

    offset = getTimeZoneOffset(zone, when)
    if offset >= 0:
        when = when - timedelta(hours=offset)
    else:
        when = when + timedelta(hours=offset)
    if tz_aware:
        return pytz.timezone(zone).localize(when)
        # return when.replace(tzinfo=pytz.timezone(zone))
    return when


def convertToUTC(zone, when=None):
    # this works because it gets around the issue with naive vs aware
    offset = getTimeZoneOffset(zone, when)
    if offset >= 0:
        when = when + timedelta(hours=offset)
    else:
        when = when - timedelta(hours=offset)
    return when


def convertToUTCEx(zone, when):
    local = pytz.timezone(zone)
    local_dt = local.localize(when, is_dst=None)
    return local_dt.astimezone(pytz.utc)


def getUTC(zone, when=None):
    timezone = pytz.timezone(zone)
    if when is None:
        when = datetime.today()
    return timezone.utcoffset(when)


def getTimeZoneOffset(zone, when=None, hour=None, dst=True):
    if zone is None:
        zone = "UTC"
    timezone = pytz.timezone(zone)
    if not when:
        when = datetime.today()
    timestamp = when
    if hour != None:
        when = when.replace(tzinfo=pytz.UTC, hour=hour)
    else:
        hour = 0
        when = when.replace(tzinfo=pytz.UTC)

    offset = int(when.astimezone(timezone).utcoffset().total_seconds()/3600)
    if not dst:
        offset = when.astimezone(timezone).utcoffset() - timezone.dst(timestamp)
        offset = int(offset.total_seconds()/3600)
    # if hour != None:
    offset = abs(offset) + hour
    if offset >= 24:
        offset -= 24
    return offset


def diffNow(dt):
    return diffSeconds(datetime.now(), dt)


def diffSeconds(t1, t2):
    return (t1 - t2).total_seconds()


def diffMinutes(t1, t2):
    diff = t1 - t2
    days, seconds = diff.days, diff.seconds
    hours = (days * 24)
    return (seconds / 60) + (hours * 60)


def diffHours(t1, t2):
    return diffMinutes(t1, t2) / 60


def next_weekday(d, weekday):
    return d + timedelta(days=((weekday - d.weekday()) + 7) % 7)


def prev_weekday(d, weekday):
    return d - timedelta(days=((d.weekday() - weekday) + 7) % 7)


def getWeek(start, start_day=0):
    # TODO allow selection of start day of week, where Monday is 0 and Sunday is 6
    # get records between last Monday and next Sunday
    week_start = start + timedelta(days=-start.weekday())
    week_end = start + timedelta(days=-start.weekday() - 1, weeks=1)
    return week_start, week_end


def getStartOfMonth(d, clear_time=False):
    if clear_time:
        return d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return d.replace(day=1)


def nextMonth(d):
    return getStartOfMonth(getStartOfMonth(d) + timedelta(days=32))


def getEndOfMonthNoTime(start):
    start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=calendar.monthrange(start.year, start.month)[1])
    end = end.replace(hour=0, minute=0, second=0, microsecond=0)
    return end


def getEndOfMonth(d, clear_time=False):
    if clear_time:
        return getEndOfMonthNoTime(d)
    return getStartOfMonth(nextMonth(d)) - timedelta(days=1) 


def parseDate(date_str, is_future=False, is_past=False, month_end=True, as_date=False):
    res = parseDateTime(date_str, is_future, is_past, month_end)
    if as_date and res:
        return date(res.year, res.month, res.day)
    return res


def parseDateTime(date_str, is_future=False, is_past=False, month_end=True):
    if isinstance(date_str, str):
        dt = None
        if len(date_str) > 6 and date_str.count('.') <= 1 and date_str.split('.')[0].isdigit():
            try:
                f = float(date_str)
                return datetime.utcfromtimestamp(f)
            except Exception as err:
                print(err)
        else:
            fix_month = False
            if date_str.count('-') or date_str.count('/') or date_str.count(' ') or date_str.count('.'):
                dts = re.split('/|-| |\.', date_str)
                if len(dts) == 2:
                    date_str = "{0}-{1}-01".format(dts[0], dts[1])
                else:
                    "-".join(dts)
            elif len(date_str) == 4:
                fix_month = month_end
                date_str = date_str[:2] + "-01-" + date_str[2:4]
            elif len(date_str) == 3:
                date_str = date_str[0] + "/1/" + date_str[-2:]
            elif len(date_str) == 6:
                date_str = date_str[:2] + "-" + date_str[2:4] + "-" + date_str[4:6]
        try:
            # print "parse date: {}".format(date_str)
            dt = date_parser(date_str)
            if is_future and dt.year < 2000:
                dt = dt.replace(year=dt.year+100)
            elif is_past and dt.year >= 2000:
                dt = dt.replace(year=dt.year-100)
            # print dt
            if fix_month:
                dt = dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])
            # print dt
            return dt
        except BaseException:
            pass

    elif isinstance(date_str, (date, datetime)):
        return date_str
    elif isinstance(date_str, (float, int)):
        return datetime.utcfromtimestamp(date_str)
    return None


def getDateRangeZ(start, end=None, kind=None, zone=None, hour=0, eod=None, end_eod=None):
    return getDateRange(start, end, kind, zone, hour, eod, end_eod)


def getDateRange(start, end=None, kind=None, zone=None, hour=0, eod=None, end_eod=None):
    if start is None:
        start = datetime.now()
    if zone is None or zone == "":
        zone = "UTC"
    if start == end:
        end = None
    if eod is not None:
        hour = eod

    start = parseDate(start)
    if start is None:
        raise Exception(f"invalid date format {start}")
    if end:
        end = parseDate(end)
        if start == end:
            end = None

    if kind and kind != "second":
        start = start.replace(minute=0, second=0, microsecond=0)
        if kind == "hour":
            end = start + timedelta(hours=1)
        elif kind == "day":
            start = start.replace(hour=0)
            end = start + timedelta(days=1)
        elif kind == "week":
            start = start.replace(hour=0)
            start, end = getWeek(start)
        elif kind == "month":
            start = start.replace(hour=0, day=1)
            end = getEndOfMonth(start, True)
        elif kind == "year":
            start = start.replace(hour=0, day=1, month=1)
            end = getEndOfMonth(start.replace(month=12), True)
        elif isinstance(kind, int) or (isinstance(kind, str) and kind.isdigit()):
            end = start + timedelta(days=1)
            start = end - timedelta(days=int(kind))
    
    if end is None:
        end = start + timedelta(hours=24)

    if zone and zone.lower() == "utc":
        zone = None
        if not kind and eod:
            hour = None
    # now lets convert our times to the zone
    if zone or hour:
        if zone is None:
            zone = "UTC"
        offset = getTimeZoneOffset(zone, start, hour=hour)
        if offset:
            start = start + timedelta(hours=offset)
        if end_eod:
            hour = end_eod
        offset = getTimeZoneOffset(zone, end, hour=hour)
        if offset:
            end = end + timedelta(hours=offset)
    return start, end


def convert_to_epoch_range(start, end=None):
    """
    Convert start and end times to epoch timestamps in milliseconds.

    Parameters:
    start (int, datetime, or str): The start time, which can be:
        - An int representing the epoch time in milliseconds.
        - A datetime object representing the start time.
        - A string representing a timedelta relative to the end time. The string can end with:
            - 'm' for minutes (e.g., '30m' for 30 minutes ago)
            - 'h' for hours (e.g., '5h' for 5 hours ago)
            - 'd' for days (e.g., '2d' for 2 days ago)
    end (datetime or None): The end time, which can be:
        - A datetime object representing the end time.
        - None, in which case the current time (UTC) is used.

    Returns:
    tuple: A tuple containing two integers:
        - start_epoch: The epoch time of the start parameter in milliseconds.
        - end_epoch: The epoch time of the end parameter in milliseconds.

    Raises:
    ValueError: If the end parameter is not a datetime object or None.
    ValueError: If the start parameter is not an int, datetime object, or a valid timedelta string.
    ValueError: If the start string does not end with 'm', 'h', or 'd'.

    Examples:
    >>> start = "30m"
    >>> end = datetime(2024, 5, 13, 12, 30, tzinfo=timezone.utc)
    >>> convert_to_epoch(start, end)
    (1715676600000, 1715681400000)

    >>> start = "1d"
    >>> end = None
    >>> convert_to_epoch(start, end)
    (1715595000000, 1715681400000)

    >>> start = "5h"
    >>> end = datetime(2024, 5, 13, 12, 30, tzinfo=timezone.utc)
    >>> convert_to_epoch(start, end)
    (1715661000000, 1715681400000)
    """
    if end is None:
        end = datetime.utcnow()

    if isinstance(end, datetime):
        end_epoch = int(end.timestamp() * 1000)
    else:
        raise ValueError("End parameter must be a datetime object or None.")

    if isinstance(start, int):
        start_epoch = start
    elif isinstance(start, datetime):
        start_epoch = int(start.timestamp() * 1000)
    elif isinstance(start, str):
        if start.endswith('m'):
            delta_minutes = int(start[:-1])
            start_datetime = end - timedelta(minutes=delta_minutes)
        elif start.endswith('h'):
            delta_hours = int(start[:-1])
            start_datetime = end - timedelta(hours=delta_hours)
        elif start.endswith('d'):
            delta_days = int(start[:-1])
            start_datetime = end - timedelta(days=delta_days)
        else:
            raise ValueError("Start string must end with 'm' for minutes, 'h' for hours, or 'd' for days.")
        
        start_epoch = int(start_datetime.timestamp() * 1000)
    else:
        raise ValueError("Start parameter must be an int, datetime object, or a string representing a timedelta.")

    return start_epoch, end_epoch


def updateTimeFromString(dt, time_string):
    # Check if the time_string is in "hour" format (e.g., "13") or 
    # "hour:minute" format (e.g., "1:32")
    if ':' in time_string:
        # Parse hour and minute
        hour, minute = map(int, time_string.split(':'))
    else:
        # Only hour is provided
        hour = int(time_string)
        minute = 0
    # Update the datetime object with the new hour and minute
    updated_dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return updated_dt
