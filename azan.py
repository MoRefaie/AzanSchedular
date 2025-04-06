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

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AzanScheduler:
    def __init__(self):
        """
        Initializes the AzanScheduler with prayer times fetcher, AppleManager, and environment configurations.
        """
        self.fetcher = PrayerTimesFetcher()
        self.manager = AppleManager()
        self.default_timetable = os.getenv("DEFAULT_TIMETABLE")  # Default timetable
        self.devices = json.loads(os.getenv("DEVICES")) # List of device identifiers from .env
        self.short_azan_switch = json.loads(os.getenv("SHORT_AZAN_SWITCHES"))   # Dictionary of prayer names and their short azan status
        self.media_folder = os.getenv("MEDIA_FOLDER")   # Media folder path
        self.azan_file_short = os.path.join(os.getcwd(), self.media_folder, os.getenv('SHORT_AZAN_FILE'))  # Short Azan file
        self.azan_file_fajr = os.path.join(os.getcwd(), self.media_folder, os.getenv('FAJR_AZAN_FILE'))  # Fajr Azan file
        self.azan_file_regular = os.path.join(os.getcwd(), self.media_folder, os.getenv('REGULAR_AZAN_FILE'))  # Regular Azan file

    async def _play_azan(self, prayer_name):
        """
        Plays the Azan on the configured devices based on the prayer name and SHORT_AZAN_SWITCHES.
        """
        short_azan_enabled = self.short_azan_switch.get(prayer_name)
        if short_azan_enabled == "On":
            azan_file = self.azan_file_short
            logging.info(f"📢 Playing Short Azan for {prayer_name} using file: {azan_file}")
        else:
            azan_file = self.azan_file_fajr if prayer_name.lower() == "fajr" else self.azan_file_regular
            logging.info(f"📢 Playing Azan for {prayer_name} using file: {azan_file}")

        await self.manager.announce(azan_file, self.devices)

    async def _schedule_next_prayer(self):
        """
        Fetches the next prayer time and schedules the Azan.
        """
        while True:
            # Fetch the next prayer
            next_prayer = self.fetcher.fetch_prayer_times(self.default_timetable)
            if "error" in next_prayer:
                logging.error(f"❌ Error fetching prayer times: {next_prayer['error']}")
                await asyncio.sleep(60)  # Retry after 1 minute
                continue

            prayer_name = next_prayer["prayer"]
            prayer_time_str = next_prayer["prayer_time"]
            prayer_time = datetime.strptime(prayer_time_str, "%Y-%m-%d %H:%M:%S %z")

            # Calculate the sleep duration
            now = datetime.now(prayer_time.tzinfo)
            sleep_duration = (prayer_time - now).total_seconds()

            if sleep_duration <= 0:
                logging.warning(f"⚠️ Skipping past prayer: {prayer_name} at {prayer_time}")
                continue

            logging.info(f"🕒 Next prayer: {prayer_name} at {prayer_time}. Sleeping for {sleep_duration} seconds.")
            await asyncio.sleep(sleep_duration)

            # Play the Azan
            await self._play_azan(prayer_name)

    def run(self):
        """
        Starts the Azan scheduler.
        """
        logging.info("📅 Starting Azan Scheduler...")
        asyncio.run(self._schedule_next_prayer())


if __name__ == "__main__":
    scheduler = AzanScheduler()
    scheduler.run()