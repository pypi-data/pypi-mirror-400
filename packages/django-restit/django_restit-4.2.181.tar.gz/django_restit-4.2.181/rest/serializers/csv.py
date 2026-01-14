from objict import objict
from io import StringIO
from django.http import StreamingHttpResponse
import csv
from rest import helpers as rh
from . import localizers


def flattenObject(obj, field_names, localize=None):
    row = []
    for f in field_names:
        d = ""
        if "__" in f:
            f = f.replace("__", ".")
        if "." in f:
            # we could use obj.getFieldValue
            keys = f.split('.')
            f1 = keys[0]
            f2 = keys[1]
            if f1 == "metadata" and hasattr(obj, "getProperty"):
                if len(keys) > 2:
                    d = obj.getProperty(keys[2], category=f2)
                else:
                    d = obj.getProperty(f2)
            elif hasattr(obj, "getFieldValue"):
                d = obj.getFieldValue(f, "t/a")
                if callable(d):
                    d = d()
            else:
                d1 = getattr(obj, f1, None)
                if d1 is not None:
                    if not hasattr(d1, f2):
                        if hasattr(d1, "first"):
                            d1 = d1.first()
                    d = getattr(d1, f2, "")
                    if callable(d):
                        d = d()               
        else:
            d = getattr(obj, f, "n/a")
            if callable(d):
                d = d()
        if d is None:
            d = "n/a"
        elif hasattr(d, "pk"):
            d = d.pk
        if localize and f in localize:
            rh.debug("localize....", localize[f])
            d = localizeValue(d, localize[f])
        else:
            d = str(d)
        row.append(d)
    return row


def localizeValue(value, localizer_name, extra=None):
    if "|" in localizer_name:
        localizer_name, extra = localizer_name.split("|")
    localizer = getattr(localizers, localizer_name, None)
    if localizer is not None:
        return localizer(value, extra)
    return value


def extractFieldNames(fields):
    header = []
    field_names = []
    for f in fields:
        if type(f) is tuple:
            r, f = f
            field_names.append(r)
        else:
            field_names.append(f)
        header.append(f)
    return header, field_names


def generateCSV(qset, fields, name, header_cols=None,
                values_list=False, output=None, stream=False, localize=None):
    a = objict()
    a.name = name
    a.file = StringIO()
    if output:
        a.file = output
    csvwriter = csv.writer(a.file)
    header, field_names = extractFieldNames(fields)
    if header_cols:
        header = header_cols
    csvwriter.writerow(header)
    if values_list:
        for row in qset.values_list(*field_names):
            row = [str(x) for x in row]
            csvwriter.writerow(row)
    else:
        rh.debug("localize.", localize)
        for obj in qset:
            csvwriter.writerow(flattenObject(obj, field_names, localize))
    if hasattr(a.file, "getvalue"):
        a.data = a.file.getvalue()
    a.mimetype = "text/csv"
    return a


def iterCsvObject(items, writer, header, field_names, localize=None):
    yield writer.writerow(header)
    for item in items:
        yield writer.writerow(flattenObject(item, field_names, localize))


def generateCSVStream(qset, fields, name, localize=None):
    import csv
    # check if we support stream mode
    header, field_names = extractFieldNames(fields)
    # rows = qset.values_list(*fields)
    pseudo_buffer = EchoWriter()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        iterCsvObject(qset, writer, header, field_names, localize=localize))


class EchoWriter(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def writeline(self, value):
        return "{}\n".format(value)

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
