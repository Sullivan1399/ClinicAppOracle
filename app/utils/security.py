import hashlib
import hmac
import base64
from cryptography.fernet import Fernet

from app.config.settings import settings

# Key setup for Fernet encryption/decryption
fernet_key = settings.DB_PASSWORD_ENC_KEY.encode()
cipher_suite = Fernet(fernet_key)

# Encrypt password function to store in token
def encrypt_db_password(plain_password: str) -> str:
    return cipher_suite.encrypt(plain_password.encode()).decode()

# Decrypt password function to retrieve original password
def decrypt_db_password(encrypted_password: str) -> str:
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

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