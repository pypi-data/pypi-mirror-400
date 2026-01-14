import json

class SecureSSOPayload:
    def __init__(self, user_data_json_base64: str, verification_hash: str, timestamp: int):
        self.user_data_json_base64 = user_data_json_base64
        self.verification_hash = verification_hash
        self.timestamp = timestamp

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)