import hmac
import hashlib
import time


def generate_signature(secret_key: str, timestamp: str) -> str:
    """Generate HMAC-SHA256 signature"""
    return hmac.new(
        secret_key.encode(),
        timestamp.encode(),
        hashlib.sha256
    ).hexdigest()


def create_auth_params(secret_key: str = "") -> dict:
    """Create authentication parameters"""
    timestamp = str(int(time.time()))
    signature = generate_signature(secret_key, timestamp) if secret_key else ""
    return {
        "timestamp": timestamp,
        "signature": signature
    }
