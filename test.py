# from prayer_times_fetcher import PrayerTimesFetcher
# import json

# fetcher = PrayerTimesFetcher()

# icci_prayers = fetcher.fetch_prayer_times("icci")
# print(json.dumps(icci_prayers, indent=4))

import os
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from prayer_times_fetcher import PrayerTimesFetcher
from apple_manager import AppleManager

# Load environment variables from .env file
load_dotenv()
x=0
while x < 10:
    x=x+1
    print(f'{x}:{os.getenv("TEST")}')
    time.sleep(1)

