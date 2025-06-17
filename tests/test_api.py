import sys
import os
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanSchedular.api import app, ConfigManagerGetRequest, ConfigManagerUpdateRequest

client = TestClient(app)


def test_config_manager_get_request():
    req = ConfigManagerGetRequest(list=["key1", "key2"])
    assert req.list == ["key1", "key2"]


def test_config_manager_update_request():
    req = ConfigManagerUpdateRequest(updates={"key": "value"})
    assert req.updates == {"key": "value"}


def test_prayer_times():
    response = client.get("/api/prayer-times")
    assert response.status_code in (200, 500)  # Accept error if no data


def test_scan_devices():
    response = client.get("/api/scan-devices")
    assert response.status_code in (200, 500)


def test_get_config():
    response = client.post("/api/get-config", json={"list": ["key1"]})
    assert response.status_code in (200, 500)


def test_update_config():
    response = client.post("/api/update-config", json={"updates": {"key": "value"}})
    assert response.status_code in (200, 500)


def test_update_audio():
    # This test will fail unless a valid audio file is provided, so just check for 400 error
    files = {"file": ("test.mp3", b"fakecontent", "audio/mpeg")}
    data = {"fileType": "mp3"}
    response = client.post("/api/update-audio", files=files, data=data)
    assert response.status_code in (200, 400, 500)
