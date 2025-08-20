import pytest

@pytest.mark.asyncio
async def test_total_jobs_count(async_client):
    res = await async_client.get("/api/v1/dashboard/total-jobs")
    assert res.status_code == 200
    assert "total_jobs" in res.json()

@pytest.mark.asyncio
async def test_total_applications_count(async_client):
    res = await async_client.get("/api/v1/dashboard/total-applications")
    assert res.status_code == 200
    assert "total_applications" in res.json()

@pytest.mark.asyncio
async def test_jobs_by_location(async_client):
    res = await async_client.get("/api/v1/dashboard/jobs-by-location")
    assert res.status_code == 200
    assert isinstance(res.json(), dict)

@pytest.mark.asyncio
async def test_applications_per_job(async_client):
    res = await async_client.get("/api/v1/dashboard/applications-per-job")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
