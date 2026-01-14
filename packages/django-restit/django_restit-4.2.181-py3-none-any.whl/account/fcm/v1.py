import json
import time
import jwt  # PyJWT library
import requests
from objict import objict
from rest import log
from rest import settings


DEBUG_FCM = settings.get("DEBUG_FCM", False)
logger = log.getLogger("fcm", filename="fcm.log")


def create_jwt(service_account_info):
    """
    Create a JWT (JSON Web Token) for service account authentication.
    
    :param service_account_info: Dictionary containing service account credentials.
    :return: JWT string.
    """
    now = int(time.time())
    payload = {
        'iss': service_account_info['client_email'],
        'sub': service_account_info['client_email'],
        'aud': 'https://oauth2.googleapis.com/token',
        'iat': now,
        'exp': now + 3600,
        'scope': 'https://www.googleapis.com/auth/firebase.messaging'
    }
    
    additional_headers = {
        'kid': service_account_info['private_key_id']
    }
    
    token = jwt.encode(payload, service_account_info['private_key'], algorithm='RS256', headers=additional_headers)
    return token

def get_access_token(jwt_token):
    """
    Exchange a JWT for an access token.
    
    :param jwt_token: JWT string.
    :return: Access token string.
    """
    url = 'https://oauth2.googleapis.com/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': jwt_token
    }
    
    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()
    return response_data['access_token']


class FirebaseNotifier:
    def __init__(self, service_account_info):
        """
        Initialize the FirebaseNotifier with the project ID and service account info.
        
        :param project_id: The project ID from Firebase project settings.
        :param service_account_info: Dictionary containing service account credentials.
        """
        self.project_id = service_account_info.get("project_id")
        self.service_account_info = service_account_info
        self.fcm_url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        self.jwt_token = None
        self._jwt_expires = 0
        self.access_token = None

    @property
    def is_jwt_expired(self):
        return time.time() > self._jwt_expires
    
    
    def _get_access_token(self):
        """
        Get the access token, refreshing if necessary.
        
        :return: Access token string.
        """
        if not self.jwt_token or self.is_jwt_expired:
            self.jwt_token = create_jwt(self.service_account_info)
            self._jwt_expires = time.time() + 3000
            self.access_token = get_access_token(self.jwt_token)
        return self.access_token
    
    def send(self, registration_token, title, body, data=None, **kwargs):
        """
        Send a notification to the specified registration token.
        
        :param registration_token: Device registration token.
        :param title: Title of the notification.
        :param body: Body of the notification.
        :param data: Optional data payload to send along with the notification.

        :param ttl: optional life of message in seconds 
        :return: Response from the FCM server.
        """
        access_token = self._get_access_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        message = dict(token=registration_token)
        if title and body:
            message["notification"] = dict(title=title, body=body)
        if data:
            priority = kwargs.get("priority", None)
            message["data"] = {k:str(v) for k,v in data.items()}
            # if priority == "high":
            #     message["android"] = dict(priority="high")
            #     message["apns"] = dict(headers={"apns-priority": "10"})
            # else:
            #     message["android"] = dict(priority="normal")
            #     message["apns"] = dict(headers={"apns-priority": "5"})
        payload = dict(message=message)
        if DEBUG_FCM:
            logger.info("request", payload)
        resp = requests.post(self.fcm_url, headers=headers, data=json.dumps(payload))
        if DEBUG_FCM:
            logger.info("response", resp.json())
        return resp
