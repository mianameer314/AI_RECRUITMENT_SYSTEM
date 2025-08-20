import pytest

@pytest.mark.asyncio
async def test_list_jobs(async_client):
    res = await async_client.get("/api/v1/jobs/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

# Optional: if you have a test admin token
@pytest.mark.asyncio
async def test_create_job_as_admin(async_client):
    # Admin login
    res = await async_client.post("/api/v1/auth/login", json={
        "username": "adminuser",
        "password": "adminpass"
    })
    if res.status_code != 200:
        pytest.skip("Admin login failed (admin account might not exist)")
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "title": "AI Engineer",
        "description": "Build LLM pipelines",
        "skills": ["Python", "ML"],
        "salary": "100k"
    }

    res = await async_client.post("/api/v1/jobs/", json=job_data, headers=headers)
    assert res.status_code == 200 or res.status_code == 201
    job = res.json()
    assert job["title"] == "AI Engineer"
