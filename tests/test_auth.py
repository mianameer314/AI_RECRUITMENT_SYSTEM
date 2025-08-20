import pytest

@pytest.mark.asyncio
async def test_register_and_login(async_client):
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "candidate"
    }

    res = await async_client.post("/api/v1/auth/register", json=register_data)
    assert res.status_code == 201

    login_data = {
        "username": "testuser",
        "password": "test123"
    }

    res = await async_client.post("/api/v1/auth/login", json=login_data)
    assert res.status_code == 200
    json_data = res.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"
