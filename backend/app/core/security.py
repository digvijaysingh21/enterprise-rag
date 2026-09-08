from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password for storage.
    bcrypt automatically generates and embeds a random salt in the hash,
    so we never need to store the salt separately.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check a plaintext password against a stored bcrypt hash.
    Never decrypt a hash to compare — bcrypt hashes are one-way;
    you re-hash the input with the same salt (extracted from the stored hash)
    and compare the results.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(subject: str, role: str) -> str:
    """
    Create a signed JWT. `subject` is the user id (as a string),
    `role` is embedded as a claim so protected routes can check it
    without a DB lookup on every request.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT. Raises jose.JWTError if invalid/expired —
    callers are responsible for turning that into an HTTP 401.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])