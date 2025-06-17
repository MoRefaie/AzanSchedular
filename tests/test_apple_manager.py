import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from AzanSchedular.apple_manager import AppleManager

@pytest.mark.asyncio
async def test_discover_device_returns_none_if_not_found():
    manager = AppleManager()
    with patch("pyatv.scan", new=AsyncMock(return_value=[])):
        result = await manager._discover_device(MagicMock(), "id")
        assert result is None

@pytest.mark.asyncio
async def test_discover_device_returns_device():
    manager = AppleManager()
    fake_device = MagicMock()
    fake_device.name = "Test"
    fake_device.address = "1.2.3.4"
    with patch("pyatv.scan", new=AsyncMock(return_value=[fake_device])):
        result = await manager._discover_device(MagicMock(), "id")
        assert result == fake_device

@pytest.mark.asyncio
async def test_play_file_handles_exception():
    manager = AppleManager()
    device = MagicMock()
    device.name = "Test"
    device.address = "1.2.3.4"
    with patch("pyatv.connect", new=AsyncMock(side_effect=Exception("fail"))):
        await manager._play_file(MagicMock(), device, "file.mp3", 50)

@pytest.mark.asyncio
async def test_announce_calls_discover_and_play():
    manager = AppleManager()
    manager._discover_device = AsyncMock(return_value=MagicMock())
    manager._play_file = AsyncMock()
    await manager.announce("file.mp3", ["id1", "id2"], 50)
    assert manager._discover_device.await_count == 2
    assert manager._play_file.await_count <= 2

@pytest.mark.asyncio
async def test_scan_for_devices_returns_success():
    manager = AppleManager()
    fake_atv = MagicMock()
    fake_atv.name = "Test"
    fake_atv.address = "1.2.3.4"
    fake_atv.identifier = "mac"
    fake_atv.all_identifiers = ["id"]
    fake_atv.deep_sleep = False
    fake_atv.device_info = "info"
    fake_atv.ready = True
    fake_atv.services = []
    with patch("pyatv.scan", new=AsyncMock(return_value=[fake_atv])):
        result = await manager.scan_for_devices()
        assert result["status"] == "success"
