import uuid


async def test_register_and_login_flow(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    # Register
    register_resp = await client.post(
        "/auth/register",
        json={"email": email, "password": "testpass123", "role": "end_user"},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == email
    assert "hashed_password" not in register_resp.json()  # never leak this

    # Login
    login_resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "testpass123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token

    # Access protected route with token
    me_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email


async def test_login_with_wrong_password_fails(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/auth/register",
        json={"email": email, "password": "correctpass", "role": "end_user"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpass"},
    )
    assert resp.status_code == 401


async def test_me_without_token_is_unauthorized(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_duplicate_email_registration_fails(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    first = await client.post(
        "/auth/register",
        json={"email": email, "password": "testpass123", "role": "end_user"},
    )
    assert first.status_code == 201

    second = await client.post(
        "/auth/register",
        json={"email": email, "password": "anotherpass", "role": "end_user"},
    )
    assert second.status_code == 400