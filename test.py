from prayer_times_fetcher import PrayerTimesFetcher
import json

fetcher = PrayerTimesFetcher()

icci_prayers = fetcher.fetch_prayer_times("icci")
print(json.dumps(icci_prayers, indent=4))