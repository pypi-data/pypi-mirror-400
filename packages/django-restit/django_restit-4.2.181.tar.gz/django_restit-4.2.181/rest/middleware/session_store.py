from django.contrib.sessions.backends.base import SessionBase
from ws4redis import client as redis
from rest import settings


class SessionStore(SessionBase):
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self._exists = None

    def load(self):
        try:
            sk = self._get_or_create_session_key()
            session_data = redis.get(self.get_stored_key(sk)).decode()
            return self.decode(session_data)
        except Exception:
            pass
        # self._session_key = None
        return {}

    def exists(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        if session_key is None:
            return False
        if self._exists is None:
            self._exists = redis.exists(self.get_stored_key(session_key))
        return self._exists

    def create(self):
        self._session_key = self._get_new_session_key()
        self.save(True)
        self.modified = True
        return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        data = self.encode(self._get_session(no_load=must_create))
        sk = self._get_or_create_session_key()
        redis.set(
            self.get_stored_key(sk),
            data,
            self.get_expiry_age())
        return True

    def delete(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        if session_key:
            redis.delete(session_key)

    @classmethod
    def clear_expired(cls):
        pass

    def get_stored_key(self, session_key):
        """Return the real key name in redis storage
        @return string
        """
        prefix = settings.SESSION_REDIS_PREFIX
        if not prefix:
            return session_key
        return f"{prefix}{session_key}"
