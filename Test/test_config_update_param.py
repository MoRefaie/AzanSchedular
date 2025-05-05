import asyncio
from config_manager import ConfigUpdater
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def test_config_update_param():
    """
    Test function to call test_config_update_param and display the result.
    """
    config = ConfigUpdater()
    updates = {
        "DEFAULT_TIMETABLE":"icci",
        "SOURCES":{"icci": "https://islamireland.ie/api/timetable/","naas": "https://mawaqit.net/en/m/-34"},
        
    }

    update_env_keys_output = config.update_env_keys(updates)
    # Print the result
    print("Scan Results:")
    print(update_env_keys_output)

if __name__ == "__main__":
    # Use asyncio.run to properly manage the event loop
    asyncio.run(test_config_update_param())
