import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def safe_decode_token(token: str) -> dict | None:
    try:
        return decode_token(token)
    except JWTError:
        return None


def generate_audio_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _get_aesgcm() -> AESGCM:
    key = base64.b64decode(settings.encryption_key)
    return AESGCM(key)


def encrypt_text(value: str) -> str:
    aes = _get_aesgcm()
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, value.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_text(value: str) -> str:
    raw = base64.b64decode(value.encode("utf-8"))
    nonce, ciphertext = raw[:12], raw[12:]
    aes = _get_aesgcm()
    return aes.decrypt(nonce, ciphertext, None).decode("utf-8")
