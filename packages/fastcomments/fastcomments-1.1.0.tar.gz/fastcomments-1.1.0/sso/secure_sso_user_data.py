import json
import base64

class SecureSSOUserData:
    def __init__(self, user_id: str, email: str, username: str, avatar: str):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.avatar = avatar
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
    
    def as_json_base64(self) -> str:
        json_str = self.toJSON()
        json_bytes = json_str.encode("utf-8")
        
        result = base64.b64encode(json_bytes)
        return result.decode("utf-8")