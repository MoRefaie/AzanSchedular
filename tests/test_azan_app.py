import sys
import os
import pytest
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanSchedular import azan_app


# Patch pystray and PIL.Image to MagicMock if no display (headless CI)
no_display = not os.environ.get("DISPLAY") and sys.platform != "win32"
if no_display:
    sys.modules["pystray"] = MagicMock()
    sys.modules["PIL.Image"] = MagicMock()

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
    async def fake_start_api():
        return None, None

    async def fake_start_web():
        return "AzanUI_MISSING"

    async def fake_start_scheduler():
        return None

    async def fake_shutdown():
        return None

    monkeypatch.setattr(azan_app, "start_api", fake_start_api)
    monkeypatch.setattr(azan_app, "start_web", fake_start_web)
    monkeypatch.setattr(azan_app, "start_scheduler", fake_start_scheduler)
    monkeypatch.setattr(azan_app, "shutdown", fake_shutdown)
    await azan_app.main()


@pytest.mark.skipif(no_display, reason="No display available for GUI tests.")
def test_on_quit_sets_shutdown():
    icon = MagicMock()
    azan_app.shutdown_trigger = False
    azan_app.on_quit(icon, None)
    assert azan_app.shutdown_trigger is True
    icon.stop.assert_called_once()


@pytest.mark.skipif(no_display, reason="No display available for GUI tests.")
def test_on_open_azanui_opens_browser():
    with patch("webbrowser.open") as mock_open:
        azan_app.on_open_azanui(MagicMock(), None)
        mock_open.assert_called()


@pytest.mark.skipif(no_display, reason="No display available for GUI tests.")
def test_setup_tray_icon(monkeypatch):
    # Patch pystray.Icon to avoid running the real tray icon
    monkeypatch.setattr(azan_app, "pystray", MagicMock())
    monkeypatch.setattr(azan_app, "Image", MagicMock())
    azan_app.setup_tray_icon()
