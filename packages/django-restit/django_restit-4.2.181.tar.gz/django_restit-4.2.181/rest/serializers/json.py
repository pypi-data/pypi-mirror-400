from rest import helpers
import json
import time
import datetime
import math
from decimal import Decimal
import pprint


def serialize(data):
    return toJSON(data)


def toJSON(data, **kwargs):
    return json.dumps(data, cls=JSONEncoderExt)
    # return json.dumps(data, **kwargs)


def prettyJSON(data):
    return json.dumps(data, cls=JSONEncoderExt, sort_keys=True, indent=4, separators=(',', ': '))


def prettyJSON2(data):
    return pprint.pformat(data)


try:
    import ujson
    def toJSON(data, **kwargs):
        # helpers.log_print(data)
        return ujson.dumps(data)
except Exception:
    helpers.log_print("recommend installing ujson!")


def toString(value):
    if isinstance(value, bytes):
        value = value.decode()
    elif isinstance(value, bytearray):
        value = value.decode("utf-8")
    elif isinstance(value, (int, float)):
        value = str(value)
    return value


# is this useless??? we have rest_serialize
class JSONEncoderExt(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return time.mktime(obj.timetuple())
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y/%m/%d")
        elif isinstance(obj, Decimal):
            if obj.is_nan():
                return 0.0
            return float(obj)
        elif isinstance(obj, float):
            if math.isnan(obj):
                return 0.0
        elif isinstance(obj, set):
            # helpers.log_error(obj)
            return str(obj)
        elif isinstance(obj, (bytes, bytearray)):
            return toString(obj)
        try:
            return super().default(obj)
        except Exception:
            pass
        return "not parsable"

