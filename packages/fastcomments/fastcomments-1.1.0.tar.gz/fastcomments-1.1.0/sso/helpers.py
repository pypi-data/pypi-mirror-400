import hmac
import hashlib

class CreateHashError(Exception):
    """Error occurred during hash creation."""

def create_verification_hash(api_key: str, timestamp: int, user_data_json_base64: str):
    try:
        # Create message string by concatenating timestamp and base64 data
        message_str = f"{timestamp}{user_data_json_base64}"
        
        # Create HMAC using SHA256 hash function
        mac = hmac.new(
            key=api_key.encode('utf-8'),
            msg=message_str.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        
        # Get digest as bytes then convert to hex
        bytes_result = mac.digest()
        return get_bytes_as_hex(bytes_result)
        
    except Exception as e:
        raise CreateHashError(f"Failed to create verification hash: {str(e)}")
    
def get_bytes_as_hex(bytes_data: bytes) -> str:
    return ''.join(f'{b:02x}' for b in bytes_data)