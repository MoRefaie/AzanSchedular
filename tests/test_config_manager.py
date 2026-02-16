import sys
import os
import pytest
from unittest.mock import patch, mock_open
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanSchedular.config_manager import SystemConfigManager, ConfigManager


def test_system_config_manager_load_sys_config():
    # Ensure os.path.exists returns True for config directory and system.json
    with patch("builtins.open", mock_open(read_data='{"API_HOST": "127.0.0.1"}')):
        with patch("os.getcwd", return_value="/tmp"):
            with patch("os.path.exists", return_value=True):
                mgr = SystemConfigManager()
                assert mgr.load_sys_config("API_HOST") == "127.0.0.1"


def test_config_manager_load_and_save_config():
    with patch("builtins.open", mock_open(read_data='{"key": "value"}')) as m:
        mgr = ConfigManager()
        mgr.config_file_path = "dummy.json"
        assert mgr.load_config("key") == "value"
        assert mgr.load_config() == {"key": "value"}
    with patch("builtins.open", mock_open()) as m:
        mgr.save_config({"a": 1})
        m().write.assert_called()


def test_validate_url():
    mgr = ConfigManager()
    assert mgr._validate_url("http://example.com")
    assert not mgr._validate_url("not a url")


def test_validate_dict_switch():
    mgr = ConfigManager()
    assert mgr._validate_dict_switch({"Fajr": "On", "Sunrise": "Off", "Dhuhr": "On", "Asr": "On", "Maghrib": "Off", "Isha": "On"}, ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"])
    assert not mgr._validate_dict_switch({}, ["Fajr"])


def test_validate_single_switch():
    mgr = ConfigManager()
    assert mgr._validate_single_switch("On")
    assert not mgr._validate_single_switch(123)


def test_sanitize_sources():
    mgr = ConfigManager()
    # valid source should keep itself and ensure Default is present
    cleaned, msgs = mgr._sanitize_sources({"a": "http://x.com"})
    assert cleaned.get("a") == "http://x.com"
    assert cleaned.get("Default") == "--"
    assert msgs == []

    # invalid url should be removed but Default still present, and messages should indicate failure
    cleaned2, msgs2 = mgr._sanitize_sources({"a": "badurl"})
    assert "a" not in cleaned2
    assert cleaned2.get("Default") == "--"
    assert any("Invalid URL" in m for m in msgs2)


def test_is_validate_key():
    mgr = ConfigManager()
    assert mgr._is_validate_key("REGULAR_AZAN_FILE", "audio")
    assert not mgr._is_validate_key("BAD_KEY", "audio")


def test_get_config_values():
    mgr = ConfigManager()
    with patch.object(mgr, "load_config", return_value={"a": 1, "b": 2}):
        result = mgr.get_config_values(["a", "b", "c"])
        assert result == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_update_env_keys_invalid_key():
    mgr = ConfigManager()
    with patch.object(mgr, "_is_validate_key", return_value=False):
        result = await mgr.update_env_keys({"bad": 1})
        assert result["status"] == "fail"


@pytest.mark.asyncio
async def test_update_media_file_invalid_key():
    mgr = ConfigManager()
    with patch.object(mgr, "_is_validate_key", return_value=False):
        result = await mgr.update_media_file("file.mp3", "BAD_KEY", b"bytes")
        assert result["status"] == "fail"
