import requests
from objict import objict
from rest import __version__ as restit_version
from urllib.parse import urlparse, parse_qs, urlunparse
from rest import helpers as rh

def getURL(host, path):
    if path is None:
        return host
    if host.endswith("/"):
        host = host[:-1]
    if path.startswith("/"):
        path = path[1:]
    if host.startswith("http"):
        return "{host}/{path}"
    return f"https://{host}/{path}" 


def REQUEST(method, host, path=None, data=None, params=None, 
            headers=None, files=None, session=None, post_json=False,
            timeout=None, verify=True, raw_response=False):
    url = getURL(host, path)
    if headers is None:
        headers = objict()

    fields = dict(url=url, params=params, files=files, verify=verify, timeout=timeout)
    if isinstance(data, dict):
        post_json = True
        fields["json"] = objict.fromdict(data).toJSON()
    elif data is not None:
        fields["data"] = data

    # headers["Accept"] = 'application/json'
    if post_json:
        headers['Content-type'] = 'application/json'
    if "User-Agent" not in headers:
        headers["User-Agent"] = f"restit/{restit_version}"
    fields["headers"] = headers
    if session is None:
        session = requests

    rh.debug("net.REQUEST", fields)
    if raw_response:
        return getattr(session, method.lower())(**fields)

    try:
        res = getattr(session, method.lower())(**fields)
    except Exception as err:
        return objict(status=False, status_code=500, error=str(err))
    return processResponse(res, url)


def processResponse(res, url):
    data = res.text
    try:
        data = objict.fromdict(res.json())
    except Exception as err:
        return objict(status=False, status_code=res.status_code, data=res.text, error=str(err))

    if res.status_code not in [200, 201]:
        if isinstance(data, dict) and data.error:
            data.status = False
            data.status_code = res.status_code
            return data
        return objict(status=False, status_code=res.status_code, error=res.text)
    if data.data:
        data = data.data
    return objict(status=True, status_code=res.status_code, data=data)


def parse_params(url):
    """
    Extracts the base URL (without parameters) and parameters from a URL.

    Parameters:
    - url (str): The URL from which to extract the base URL and parameters.

    Returns:
    - tuple: A tuple containing the base URL (str) and a dictionary of parameters.
    """
    # Parse the URL
    parsed_url = urlparse(url)
    # Extract and convert the query part to a dictionary
    params = parse_qs(parsed_url.query)
    # Convert the values lists to single values if they contain only one item
    params_single_value = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
    # Reconstruct the URL without the query part
    base_url = urlunparse(parsed_url._replace(query=""))
    return base_url, params_single_value
