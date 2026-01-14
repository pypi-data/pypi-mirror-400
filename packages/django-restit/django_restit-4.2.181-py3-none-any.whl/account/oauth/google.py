from rest import settings
import requests
from rest import helpers as rh
from objict import objict

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def validateIdToken(id_token) -> bool:
    # Reference: https://developers.google.com/identity/sign-in/web/backend-auth#verify-the-integrity-of-the-id-token
    response = requests.get(
        GOOGLE_ID_TOKEN_INFO_URL,
        params={'id_token': id_token}
    )

    if not response.ok:
        raise Exception('id_token is invalid.')

    audience = response.json()['aud']

    if audience != settings.GOOGLE_OAUTH2_CLIENT_ID:
        raise Exception('Invalid audience.')

    return True


def getAccessToken(code, redirect_uri):
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        rh.log_error("google.getAccessToken FAILED", data, "response", response.text)
        return None
    resp = response.json()
    # rh.log_print("getAccessToken", resp)
    return objict.fromdict(resp)


def getUserInfo(access_token):
    """
    Get user information from Google

    :param access_token: Google access token
    :return: User info
    """
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )
    if not response.ok:
        rh.log_error("google.getUserInfo FAILED", response.text)
        return None
    resp = objict.fromdict(response.json())
    # rh.log_print("getUserInfo", resp)
    return resp
