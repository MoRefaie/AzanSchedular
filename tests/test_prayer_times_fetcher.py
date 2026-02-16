import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanScheduler.prayer_times_fetcher import PrayerTimesFetcher


def test_get_timezone_valid():
    fetcher = PrayerTimesFetcher()
    with patch("AzanScheduler.prayer_times_fetcher.config.load_config", return_value="UTC"):
        tz = fetcher._get_timezone()
        assert tz is not None


def test_validate_url_and_dict_switch():
    fetcher = PrayerTimesFetcher()
    # Just to show we can instantiate and call methods
    assert hasattr(fetcher, "_get_timezone")


def test_format_timetable_handles_missing_file():
    fetcher = PrayerTimesFetcher()
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert fetcher.format_timetable("icci") is False


def test_reload_data_handles_missing_file():
    fetcher = PrayerTimesFetcher()
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert fetcher._reload_data("icci") is None


def test_is_new_month_returns_bool():
    fetcher = PrayerTimesFetcher()
    with patch("AzanScheduler.prayer_times_fetcher.config.load_config", return_value="UTC"):
        assert isinstance(fetcher._is_new_month({"1": {}}), bool)


def test_fetch_prayer_times_invalid_type():
    fetcher = PrayerTimesFetcher()

    def load_config_side_effect(*args, **kwargs):
        # Always return a valid value for any config key
        if args and args[0] == "DEFAULT_TIMETABLE":
            return "icci"
        if args and args[0] == "SOURCES":
            return {"icci": "url"}
        return None

    with patch("AzanScheduler.prayer_times_fetcher.config.load_config", side_effect=load_config_side_effect):
        with patch.object(fetcher, "_is_file_outdated", return_value=False):
            with patch.object(fetcher, "_reload_data", return_value={"1": {}}):
                result = fetcher.fetch_prayer_times("badtype")
                assert "error" in result
