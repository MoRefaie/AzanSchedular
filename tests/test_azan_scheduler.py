import sys
import os
import pytest
from unittest.mock import patch, AsyncMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanSchedular.azan_scheduler import AzanScheduler


def test_azan_scheduler_init():
    scheduler = AzanScheduler()
    assert scheduler.fetcher is not None
    assert scheduler.manager is not None


@pytest.mark.asyncio
async def test_play_azan_calls_announce():
    scheduler = AzanScheduler()
    scheduler.manager.announce = AsyncMock()
    with patch("AzanSchedular.azan_scheduler.config.load_config") as mock_load:
        # Setup config values for all required keys
        mock_load.side_effect = lambda key=None: {
            "DEVICES": ["dev1"],
            "AZAN_SWITCHES": {"fajr": "On"},
            "SHORT_AZAN_SWITCHES": {"fajr": "Off"},
            "DUAA_SWITCHES": {"fajr": "Off"},
            "ISHA_GAMA_SWITCH": "Off",
            "SHORT_AZAN_FILE": "short.mp3",
            "FAJR_AZAN_FILE": "fajr.mp3",
            "REGULAR_AZAN_FILE": "reg.mp3",
            "DUAA_FILE": "duaa.mp3",
            "AUDIO_VOLUME": 50
        }[key]
        with patch("os.path.exists", return_value=True):
            await scheduler._play_azan("fajr")
    scheduler.manager.announce.assert_called()
