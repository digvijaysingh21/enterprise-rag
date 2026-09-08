from app.core.security import hash_password, verify_password


def test_password_hash_and_verify_roundtrip():
    plain = "mysecretpassword"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_rejects_wrong_password():
    hashed = hash_password("correctpassword")
    assert verify_password("wrongpassword", hashed) is False