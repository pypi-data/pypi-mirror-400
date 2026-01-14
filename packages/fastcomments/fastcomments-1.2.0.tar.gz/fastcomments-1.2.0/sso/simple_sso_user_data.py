import json

class SimpleSSOUserData:
    def __init__(self, user_id: str, email: str, avatar: str):
        self.user_id = user_id
        self.email = email
        self.avatar = avatar
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)