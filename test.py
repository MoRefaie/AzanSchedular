# from prayer_times_fetcher import PrayerTimesFetcher
# import json

# fetcher = PrayerTimesFetcher()

# icci_prayers = fetcher.fetch_prayer_times("icci")
# print(json.dumps(icci_prayers, indent=4))

import os
import asyncio
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from prayer_times_fetcher import PrayerTimesFetcher
from apple_manager import AppleManager

# Load environment variables from .env file
load_dotenv()

devices = json.loads(os.getenv("DEVICES"))
print(os.getcwd())
manager = AppleManager()
file_to_play = f"{os.getcwd()}\media\ShortAthan.mp3"


asyncio.run(manager.announce(file_to_play, devices))