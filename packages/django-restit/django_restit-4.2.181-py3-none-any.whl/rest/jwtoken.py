import jwt
from objict import objict
import time
import uuid
from rest import settings

JWT_EXP_6_HOURS = 21600
JWT_EXP_12_HOURS = 43200
JWT_EXP_1_DAY = 86400
JWT_EXP_2_DAY = 172800
JWT_EXP_7_DAY = 604800
JWT_EXP_30_MIN = 1800
JWT_EXP_15_MIN = 900
JWT_KEY = settings.SECRET_KEY
JWT_EXPIRES = settings.get("JWT_EXPIRES", JWT_EXP_30_MIN)
JWT_REFRESH_EXPIRES = settings.get("JWT_REFRESH_EXPIRES", JWT_EXP_2_DAY)


class JWToken():
    def __init__(self, token=None, user_id=None, key=JWT_KEY, 
                 device_id=None, alg="HS256", access_expires_in=JWT_EXPIRES,
                 refresh_expires_in=JWT_REFRESH_EXPIRES):
        # takes full JWT token header.payload.signature
        self.token = token
        self.key = key
        self.alg = alg
        self.access_expires_in = access_expires_in
        self.refresh_expires_in = refresh_expires_in
        self._is_valid = None
        if token is None:
            self.payload = objict(token_type="access", jti=uuid.uuid4().hex)
            if user_id is not None:
                self.payload["user_id"] = user_id
            if device_id is not None:
                self.payload["device_id"] = device_id
            self.refresh()
        else:
            self.payload = objict.fromdict(jwt.decode(token, key, algorithms=alg, options=dict(verify_signature=False)))
            
    @property
    def is_valid(self):
        if self._is_valid is not None:
            return self._is_valid
        try:
            objict.fromdict(jwt.decode(self.token, self.key, algorithms=self.alg))
            self._is_valid = True
        except Exception:
            self._is_valid = False
        return self._is_valid

    @property
    def session_id(self):
        if self.payload:
            return self.payload.jti
        return None

    def isExpired(self):
        if self.payload.exp is None:
            return False
        return self.payload.exp > time.time()

    def refresh(self, expires_in=None):
        self.payload["token_type"] = "access"
        self.payload["iat"] = int(time.time())
        if expires_in is None:
            expires_in = self.access_expires_in
        self.payload["exp"] = int(time.time()) + expires_in

    @property
    def access_token(self):
        return jwt.encode(self.payload, self.key, algorithm=self.alg)

    @property
    def refresh_token(self):
        r_payload = objict.fromdict(self.payload)
        r_payload["token_type"] = "refresh"
        r_payload["exp"] = int(time.time()) + self.refresh_expires_in
        return jwt.encode(r_payload, self.key)


