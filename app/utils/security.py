import hashlib
import hmac

from app.config.settings import settings

# Hash password function by HMAC-SHA256 (HS256)
def hash_password(plain_password: str) -> str:
    key = settings.SECRET_KEY.encode('utf-8')
    msg = plain_password.encode('utf-8')
    
    # Create HMAC hash
    hashed = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return hashed

# Function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password