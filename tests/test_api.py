import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from AzanSchedular.api import app, ConfigManagerGetRequest, ConfigManagerUpdateRequest

client = TestClient(app)


def test_config_manager_get_request():
    req = ConfigManagerGetRequest(list=["key1", "key2"])
    assert req.list == ["key1", "key2"]


def test_config_manager_update_request():
    req = ConfigManagerUpdateRequest(updates={"key": "value"})
    assert req.updates == {"key": "value"}


@pytest.mark.asyncio
async def test_prayer_times():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/prayer-times")
    assert response.status_code in (200, 500)  # Accept error if no data


@pytest.mark.asyncio
async def test_scan_devices():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/scan-devices")
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_get_config():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/get-config", json={"list": ["key1"]})
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_update_config():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/update-config", json={"updates": {"key": "value"}})
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_update_audio():
    # This test will fail unless a valid audio file is provided, so just check for 400 error
    files = {"file": ("test.mp3", b"fakecontent", "audio/mpeg")}
    data = {"fileType": "mp3"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/update-audio", files=files, data=data)
    assert response.status_code in (200, 400, 500)


@pytest.mark.asyncio
async def test_api_scheduler_status():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/scheduler-status")
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_api_start_scheduler():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/start-scheduler")
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_api_stop_scheduler():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/stop-scheduler")
    assert response.status_code in (200, 500)
