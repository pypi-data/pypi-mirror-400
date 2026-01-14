from rest import settings
from objict import objict
# import boto
# from boto.s3.connection import S3Connection
import boto3
import botocore

from urllib.parse import urlparse
import io
import sys
from medialib import utils
import threading
import tempfile

S3 = objict(
    KEY=settings.AWS_KEY,
    SECRET=settings.AWS_SECRET,
    REGSION=settings.AWS_REGION,
    BUCKET=settings.AWS_S3_BUCKET)


class S3Item(object):
    def __init__(self, url, content_type="application/json", metadata=None):
        self.url = url
        u = urlparse(url)
        self.bucket_name = u.netloc
        self.key = u.path.lstrip('/')
        self.content_type = content_type
        self.s3 = getS3()
        self.host = "https://s3.amazonaws.com"
        self.metadata = metadata
        self.object = getObject(self.bucket_name, self.key)
        self.exists = self.checkExists()

    def checkExists(self):
        try:
            self.object.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise
        return True

    def upload(self, fp, background=False):
        if self.metadata:
            return self.object.upload_fileobj(openFile(fp), ExtraArgs=self.metadata)
        self.object.upload_fileobj(openFile(fp))

    def createUpload(self):
        self.part_num = 0
        self.parts = []
        self.client = getS3(False)
        resp = self.client.create_multipart_upload(Bucket=self.bucket_name, Key=self.key)
        self.upload_id = resp["UploadId"]
        return True

    def uploadPart(self, chunk):
        self.part_num += 1
        resp = self.client.upload_part(
            Bucket=self.bucket_name,
            Key=self.key,
            PartNumber=self.part_num,
            UploadId=self.upload_id,
            Body=chunk)
        self.parts.append(dict(PartNumber=self.part_num, ETag=resp["ETag"]))

    def completeUpload(self):
        resp = self.client.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.key,
            UploadId=self.upload_id,
            MultipartUpload=dict(Parts=self.parts))
        return resp

    @property
    def public_url(self):
        return "{}/{}/{}".format(self.host, self.bucket_name, self.key)

    def generateURL(self, expires=600):
        client = getS3(False)
        return client.generate_presigned_url(
            'get_object',
            ExpiresIn=expires,
            Params={'Bucket': self.bucket_name, 'Key': self.key})

    def download(self, fp=None):
        if fp is None:
            fp = tempfile.NamedTemporaryFile()
        self.object.download_fileobj(fp)
        return fp

    def delete(self):
        self.object.delete()


def _getS3(as_resource=True, key=S3.KEY, secret=S3.SECRET):
    if as_resource:
        return boto3.resource('s3', aws_access_key_id=key, aws_secret_access_key=secret)
    return boto3.client('s3', aws_access_key_id=key, aws_secret_access_key=secret)


def getS3(as_resource=True):
    if as_resource:
        if S3.resource is None:
            S3.resource = _getS3(True)
        return S3.resource
    if S3.client is None:
        S3.client = _getS3(False)
    return S3.client


def getBucket(name):
    s3r = getS3()
    return s3r.Bucket(name)


def getObject(bucket_name, key):
    s3r = getS3()
    return s3r.Object(bucket_name, key)


def getObjectContent(bucket_name, key):
    s3r = getS3(False)
    obj = s3r.get_object(Bucket=bucket_name, Key=key)
    return obj['Body'].read().decode('utf-8')


class ProgressPercentage(object):
    def __init__(self, size):
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def upload(url, fp, background=False):
    obj = S3Item(url)
    obj.upload(fp)


def view_url_noexpire(url, is_secure=False):
    obj = S3Item(url)
    return obj.public_url


def view_url(url, expires=600, is_secure=True):
    if expires is None:
        return view_url_noexpire(url, is_secure)
    obj = S3Item(url)
    return obj.generateURL(expires)


def exists(url):
    obj = S3Item(url)
    return obj.exists


def get_file(url, fp=None):
    obj = S3Item(url)
    return obj.download(fp)


def generate_upload_url(url, filetype, expires=3600, acl="public-read"):
    u = urlparse(url)
    bucket_name = u.netloc
    key = u.path.lstrip('/')
    client = getS3(False)
    params = dict(Bucket=bucket_name, Key=key, ContentType=filetype)
    from rest import helpers
    helpers.log_error("generate_upload_url", params)
    return client.generate_presigned_url(
        'put_object',
        ExpiresIn=expires,
        Params=params)


def delete(url):
    if url[-1] == "/":
        prefix = url.path.lstrip("/")
        bucket_name = url.netloc
        s3 = getS3()
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix =prefix,
            MaxKeys=100)
        for obj in response['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=object['Key'])
    else:
        obj = S3Item(url)
        obj.delete()
        # _getkey(url, key=settings.AWS_ADMIN_KEY, secret=settings.AWS_ADMIN_SECRET).delete()


def openFile(fp):
    # this should fail if already opened.. if not iwll open
    # even if wrapped file-like object exists. To avoid Django-specific
    # logic, pass a copy of internal file-like object if `content` is
    # `File` class instance.
    if isinstance(fp, (str, bytes)):
        return io.BytesIO(utils.toBytes(fp))
    if hasattr(fp, "read"):
        return io.BytesIO(utils.toBytes(fp.read()))
    try:
        return open(fp.name, "r")
    except IOError:
        pass
    return fp


def path(url):
    u = urlparse(url)
    return u.path
