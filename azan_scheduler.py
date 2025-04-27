import os
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from prayer_times_fetcher import PrayerTimesFetcher
from apple_manager import AppleManager
from logging_config import get_logger  # Import the centralized logger

# Load environment variables from .env file
load_dotenv()

# Get a logger for this module
logger = get_logger(__name__)

class AzanScheduler:
    def __init__(self):
        """
        Initializes the AzanScheduler with prayer times fetcher and AppleManager.
        """
        self.fetcher = PrayerTimesFetcher()
        self.manager = AppleManager()

    async def _play_azan(self, prayer_name):
        """
        Plays the Azan on the configured devices based on the prayer name and SHORT_AZAN_SWITCHES.
        """
        # Fetch environment variables dynamically
        devices = json.loads(os.getenv("DEVICES"))  # List of device identifiers
        azan_switches = json.loads(os.getenv("AZAN_SWITCHES"))  # JSON string for prayer switches
        short_azan_switch = json.loads(os.getenv("SHORT_AZAN_SWITCHES"))  # Short Azan switches
        duaa_switch = json.loads(os.getenv("DUAA_SWITCHES"))  # Short Azan switches
        media_folder = os.getenv("MEDIA_FOLDER")  # Media folder path
        azan_file_short = os.path.join(os.getcwd(), media_folder, os.getenv('SHORT_AZAN_FILE'))
        azan_file_fajr = os.path.join(os.getcwd(), media_folder, os.getenv('FAJR_AZAN_FILE'))
        azan_file_regular = os.path.join(os.getcwd(), media_folder, os.getenv('REGULAR_AZAN_FILE'))
        duaa_file = os.path.join(os.getcwd(), media_folder, os.getenv('DUAA_FILE'))
        audio_volume = float(os.getenv("AUDIO_VOLUME"))  # Default audio volume level (0.0 to 1.0)

        # Check if Azan is enabled for the prayer
        azan_enabled = azan_switches.get(prayer_name)
        if azan_enabled == "On":
            logger.info(f"📢 Azan for {prayer_name} is enabled in the configuration.")
            short_azan_enabled = short_azan_switch.get(prayer_name)
            if short_azan_enabled == "On":
                azan_file = azan_file_short
                logger.info(f"📢 Playing Short Azan for {prayer_name} using file: {azan_file}")
            else:
                azan_file = azan_file_fajr if prayer_name.lower() == "fajr" else azan_file_regular
                logger.info(f"📢 Playing Azan for {prayer_name} using file: {azan_file}")

            await self.manager.announce(azan_file, devices, audio_volume)
            duaa_enabled = duaa_switch.get(prayer_name)
            if duaa_enabled == "On":
                logger.info(f"📢 Playing Duaa for {prayer_name} using file: {duaa_file}")
                await self.manager.announce(duaa_file, devices, audio_volume)
            else:
                logger.info(f"🔕 Duaa for {prayer_name} is disabled in the configuration.")
        else:
            logger.info(f"🔕 Azan for {prayer_name} is disabled in the configuration.")

    async def _schedule_next_prayer(self):
        """
        Fetches the next prayer time and schedules the Azan.
        """
        while True:
            # Fetch the next prayer
            next_prayer = self.fetcher.fetch_prayer_times(os.getenv("DEFAULT_TIMETABLE"))
            if "error" in next_prayer:
                logger.error(f"❌ Error fetching prayer times: {next_prayer['error']}")
                await asyncio.sleep(60)  # Retry after 1 minute
                continue

            prayer_name = next_prayer["prayer"]
            prayer_time_str = next_prayer["prayer_time"]
            prayer_time = datetime.strptime(prayer_time_str, "%Y-%m-%d %H:%M:%S %z")

            # Calculate the sleep duration
            now = datetime.now(prayer_time.tzinfo)
            sleep_duration = (prayer_time - now).total_seconds()

            if sleep_duration <= 0:
                logger.warning(f"⚠️ Skipping past prayer: {prayer_name} at {prayer_time}")
                continue

            # Calculate hours, minutes, and seconds from sleep_duration
            hours, remainder = divmod(sleep_duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Log the next prayer time with sleep duration in hours:minutes:seconds format
            logger.info(f"🕒 Next prayer: {prayer_name} at {prayer_time}. Sleeping for {int(hours):02}:{int(minutes):02}:{int(seconds):02}.")
            await asyncio.sleep(sleep_duration)

            # Play the Azan
            await self._play_azan(prayer_name)

    async def run(self):
        """
        Starts the Azan scheduler.
        """
        logger.info("📅 Starting Azan Scheduler...")
        await self._schedule_next_prayer()


if __name__ == "__main__":
    scheduler = AzanScheduler()
    asyncio.run(scheduler.run())  # Use asyncio.run() only at the top level