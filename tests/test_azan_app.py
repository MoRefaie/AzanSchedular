import pytest
import sys
import types
from unittest.mock import patch, MagicMock
import asyncio
from AzanSchedular import azan_app

@pytest.mark.asyncio
async def test_shutdown_runs():
    # Should run without error
    await azan_app.shutdown()

@pytest.mark.asyncio
async def test_start_api_handles_failure():
    with patch("uvicorn.Server.serve", new_callable=MagicMock) as mock_serve:
        mock_serve.side_effect = Exception("fail")
        server, task = await azan_app.start_api()
        assert server is None and task is None

@pytest.mark.asyncio
async def test_start_web_missing_file():
    with patch("os.path.exists", return_value=False):
        result = await azan_app.start_web()
        assert result == "AzanUI_MISSING"

@pytest.mark.asyncio
async def test_main_runs(monkeypatch):
    # Patch all sub-functions to avoid side effects
    monkeypatch.setattr(azan_app, "start_api", lambda: asyncio.sleep(0.01) or (None, None))
    monkeypatch.setattr(azan_app, "start_web", lambda: asyncio.sleep(0.01) or "AzanUI_MISSING")
    monkeypatch.setattr(azan_app, "start_scheduler", lambda: asyncio.sleep(0.01))
    monkeypatch.setattr(azan_app, "shutdown", lambda: asyncio.sleep(0.01))
    await azan_app.main()


def test_on_quit_sets_shutdown():
    icon = MagicMock()
    azan_app.shutdown_trigger = False
    azan_app.on_quit(icon, None)
    assert azan_app.shutdown_trigger is True
    icon.stop.assert_called_once()

def test_on_open_azanui_opens_browser():
    with patch("webbrowser.open") as mock_open:
        azan_app.on_open_azanui(MagicMock(), None)
        mock_open.assert_called()

def test_setup_tray_icon(monkeypatch):
    # Patch pystray.Icon to avoid running the real tray icon
    monkeypatch.setattr(azan_app, "pystray", MagicMock())
    monkeypatch.setattr(azan_app, "Image", MagicMock())
    azan_app.setup_tray_icon()
