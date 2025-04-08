import asyncio
from config_update import ConfigUpdater
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def test_config_update_param():
    """
    Test function to call test_config_update_param and display the result.
    """
    config = ConfigUpdater()
    try:
        updates = {
            "DEVICES": ["111111111111", "222222222222"],
            "DEFAULT_TIMETABLE": "nass",
            "TIMEZONE": "Eur",
            "SHORT_AZAN_SWITCHES":{"Fajr": "On", "Sunrise": "Off", "Dhuhr": "Off", "Asr": "Off", "Maghrib": "Off", "Isha": "Off"},
            "test_key": "test_value"

        }
        print(os.getenv("DEVICES"))
        print(os.getenv("DEFAULT_TIMETABLE"))
        print(os.getenv("TIMEZONE"))
        print(os.getenv("SHORT_AZAN_SWITCHES"))
        print(os.getenv("test_key"))
        update_env_keys_output = config.update_env_keys(updates)
        # Print the result
        print("Scan Results:")
        print(update_env_keys_output)
        print(os.getenv("DEVICES"))
        print(os.getenv("DEFAULT_TIMETABLE"))
        print(os.getenv("TIMEZONE"))
        print(os.getenv("SHORT_AZAN_SWITCHES"))
        print(os.getenv("test_key"))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Use asyncio.run to properly manage the event loop
    asyncio.run(test_config_update_param())
