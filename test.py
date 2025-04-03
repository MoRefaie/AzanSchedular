# from prayer_times_fetcher import PrayerTimesFetcher
# import json

# fetcher = PrayerTimesFetcher()

# icci_prayers = fetcher.fetch_prayer_times("icci")
# print(json.dumps(icci_prayers, indent=4))

from apple_manager import AppleManager
import asyncio

manager = AppleManager()
file_to_play = "https://www.gurutux.com/media/Athan.mp3"
devices = ["024203835863", "123456789012"]  # Replace with actual device identifiers

asyncio.run(manager.announce(file_to_play, devices))