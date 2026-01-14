import time

from .helpers import create_verification_hash
from .secure_sso_payload import SecureSSOPayload
from .secure_sso_user_data import SecureSSOUserData
from .simple_sso_user_data import SimpleSSOUserData


class FastCommentsSSO:
    def __init__(self, secure_sso_payload, simple_sso_user_data, login_url: str | None = None, logout_url: str | None = None):
        self.secure_sso_payload = secure_sso_payload
        self.simple_sso_user_data = simple_sso_user_data
        self.login_url = login_url
        self.logout_url = logout_url
        self.cached_token = None

    @classmethod
    def new_secure(cls, api_key: str, secure_sso_user_data: SecureSSOUserData):
        timestamp = int(time.time())

        user_data_str = secure_sso_user_data.as_json_base64()
        hash = create_verification_hash(api_key, timestamp, user_data_str)

        payload = SecureSSOPayload(user_data_str, hash, timestamp)
        return cls(secure_sso_payload = payload, simple_sso_user_data = None)

    @classmethod
    def new_simple(cls, simple_sso_user_data: SimpleSSOUserData):
        return cls(secure_sso_payload = None, simple_sso_user_data = simple_sso_user_data)

    @classmethod
    def new_secure_with_urls(
        cls, secure_sso_payload: SecureSSOPayload,
        login_url: str,
        logout_url: str,
    ):
        return cls(secure_sso_payload, None, login_url, logout_url)

    def create_token(self):
        if self.secure_sso_payload:
            return self.secure_sso_payload.toJSON()
        elif self.simple_sso_user_data:
            return self.simple_sso_user_data.toJSON()
        else:
            raise ValueError("No user data provided")

    def reset_token(self):
        self.cached_token = None
    
    def prepare_to_send(self):
        if self.cached_token:
            return self.cached_token
            
        self.cached_token = self.create_token()
        return self.cached_token
    
    def set_secure_sso_payload(self, secure_sso_payload: SecureSSOPayload):
        self.secure_sso_payload = secure_sso_payload
        self.simple_sso_user_data = None
        self.reset_token()
    
    def set_simple_sso_user_data(self, simple_sso_user_data: SimpleSSOUserData):
        self.simple_sso_user_data = simple_sso_user_data
        self.secure_sso_payload = None
        self.reset_token()