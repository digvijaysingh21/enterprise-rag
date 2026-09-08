import bcrypt


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