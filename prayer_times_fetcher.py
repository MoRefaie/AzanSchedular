import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil import tz
import requests
import json
import logging
from bs4 import BeautifulSoup
import re
import tempfile
from tenacity import retry, stop_after_attempt, wait_fixed
import time
from logging_config import get_logger  # Import the centralized logger

# Load environment variables from .env file
load_dotenv()

# Get a logger for this module
logger = get_logger(__name__)


class PrayerTimesFetcher:
    def _get_timezone(self):
        """
        Dynamically fetches the timezone from the environment.
        """
        timezone = os.getenv("TIMEZONE")
        tz_info = tz.gettz(timezone)
        if tz_info is None:
            raise ValueError(f"Invalid timezone: {timezone}")
        return tz_info

    # Download the timetable for Location
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _download_timetable(self, location):
        """
        Downloads the timetable for the specified location.
        """
        sources_url = json.loads(os.getenv("SOURCES")) # API URLs

        # Dynamically construct the timetable file path
        timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_timetable.json")

        logger.debug(f"Attempting to download {location.upper()} timetable.")
        try:
            response = requests.get(sources_url[location], timeout=10)
            response.raise_for_status()
            if location == "icci":
                data = response.json()
            elif location == "naas":
                soup = BeautifulSoup(response.text, "html.parser")
                script_tags = soup.find_all("script")
                calendar_data = None
                for script in script_tags:
                    if "calendar" in script.text:
                        match = re.search(r'"calendar"\s*:\s*(\[\{.*?\}\])', script.text, re.DOTALL)
                        if match:
                            calendar_data = match.group(1)
                        break
                if not calendar_data:
                    logger.error(f"❌ Calendar data not found in Naas webpage.")
                    return False
                data = json.loads(calendar_data)
            else:
                logger.error(f"Invalid location: {location}")
                return False

            # Save the timetable data to the file
            with open(timetable_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            logger.info(f"✅ {location.upper()} timetable downloaded and saved successfully.")
            return True
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to download {location.upper()} timetable: {e}.")
            return False
 
    # Format the timetable
    def format_timetable(self, location):
        """
        Formats the downloaded timetable into a new JSON structure as:
        {Month: {Day: {Prayer Name: Time}}}
        """
        # Dynamically construct the timetable file path
        timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_timetable.json")
        try:
            with open(timetable_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to load timetable file for {location.upper()}: {e}")
            return False

        formatted_timetable = {}

        if location == "icci":
            # Format ICCI timetable
            if not data or "timetable" not in data:
                logger.error(f"❌ Timetable data for {location.upper()} is missing or invalid.")
                return False

            # Iterate through the data
            for month, days in data["timetable"].items():
                formatted_timetable[month] = {}
                for day, prayers in days.items():
                    if len(prayers) < 6:
                        logger.warning(f"⚠️ Invalid prayer data for {location.upper()} on {month}-{day}: {prayers}")
                        continue
                    formatted_timetable[month][day] = {
                        "Fajr": f"{prayers[0][0]:02}:{prayers[0][1]:02}",
                        "Sunrise": f"{prayers[1][0]:02}:{prayers[1][1]:02}",
                        "Dhuhr": f"{prayers[2][0]:02}:{prayers[2][1]:02}",
                        "Asr": f"{prayers[3][0]:02}:{prayers[3][1]:02}",
                        "Maghrib": f"{prayers[4][0]:02}:{prayers[4][1]:02}",
                        "Isha": f"{prayers[5][0]:02}:{prayers[5][1]:02}"
                    }

        elif location == "naas":
            # Format Naas timetable
            if not data or not isinstance(data, list):
                logger.error(f"❌ Timetable data for {location.upper()} is missing or invalid.")
                return False

            # Iterate through the data
            for month, month_data in enumerate(data, start=1):
                formatted_timetable[month] = {}
                for day, prayers in month_data.items():
                    if len(prayers) < 6:
                        logger.warning(f"⚠️ Invalid prayer data for {location.upper()} on {month}-{day}: {prayers}")
                        continue
                    formatted_timetable[month][day] = {
                        "Fajr": f"{prayers[0]}",
                        "Sunrise": f"{prayers[1]}",
                        "Dhuhr": f"{prayers[2]}",
                        "Asr": f"{prayers[3]}",
                        "Maghrib": f"{prayers[4]}",
                        "Isha": f"{prayers[5]}"
                    }

        else:
            logger.error(f"❌ Unsupported location: {location}")
            return False

        # Save the formatted timetable to a new JSON file
        formatted_file_path = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_formatted_timetable.json")
        try:
            with open(formatted_file_path, "w", encoding="utf-8") as file:
                json.dump(formatted_timetable, file, indent=4, ensure_ascii=False)
            logger.info(f"✅ Formatted timetable for {location.upper()} saved successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to save formatted timetable for {location.upper()}: {e}")
            return False

        return True

    # Reload the timetable data from the file
    def _reload_data(self, location):
        """
        Reloads the timetable data from the file for the specified location.
        """
        # Dynamically construct the timetable file path
        timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_formatted_timetable.json")

        try:
            with open(timetable_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {location.upper()} timetable: {e}.")
            return None

    # Refresh the timetable
    def _refresh_timetable(self, location):
        """
        Refreshes the timetable for the specified location by downloading and formatting it.
        """
        logger.info(f"🔄 Refreshing timetable for {location.upper()}.")

        # Step 1: Download the timetable
        if not self._download_timetable(location):
            logger.error(f"❌ Failed to download timetable for {location.upper()}.")
            return False

        # Step 2: Format the downloaded timetable
        if not self.format_timetable(location):
            logger.error(f"❌ Failed to format timetable for {location.upper()}.")
            return False

        logger.info(f"✅ Timetable for {location.upper()} successfully refreshed and formatted.")
        return True

    # Check if the timetable file is outdated
    def _is_file_outdated(self, location):
        """
        Checks if the timetable file is outdated.
        """
        # Dynamically construct the timetable file path
        timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_formatted_timetable.json")

        try:
            # Get the file's last modification time
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(timetable_file), tz=self._get_timezone())
            today = datetime.now(self._get_timezone())
            last_day_of_previous_month = today.replace(day=1) - timedelta(days=1)

            # Check if the file was modified in the current month or on the last day of the previous month
            if file_mod_time >= last_day_of_previous_month:
                return False  # File is up-to-date
            return True  # File is outdated
        except FileNotFoundError:
            logger.warning(f"File {timetable_file} not found. It will be treated as outdated.")
            return True  # Treat missing file as outdated
   
    # Wait until midnight
    def _wait_until_midnight(self):
        """
        Sleeps until midnight.
        """
        now = datetime.now(self._get_timezone())
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (midnight - now).total_seconds()
        logger.info(f"Sleeping for {seconds_until_midnight} seconds until midnight.")
        time.sleep(seconds_until_midnight)

    # Get prayer times for a specific day
    def _get_day_prayers(self, data, day, month, date_text, location):
        """
        Fetches prayer times for a specific day and month from the timetable data.
        If the day is missing, attempts to refresh the timetable once.
        If still missing, waits until the end of the day to retry refreshing.
        """
        if month not in data or day not in data[month]:
            logger.warning(f"{location.upper()} data missing for {date_text}. Attempting to refresh the timetable.")
            if not self._refresh_timetable(location):
                self._wait_until_midnight()
                if not self._refresh_timetable(location):
                    logger.error(f"{location.upper()} data for {date_text} is still missing after retry. Giving up.")
                    return {"error": f"{location.upper()} data missing for {date_text}. Please check the timetable source."}
            data = self._reload_data(location)
            if month not in data or day not in data[month]:
                logger.error(f"{location.upper()} data for {date_text} is still missing after retry. Giving up.")
                return {"error": f"{location.upper()} data missing for {date_text}. Please check the timetable source."}
        return self._extract_day_prayers(data, day, month, date_text, location)

    # Extract prayer times for a specific day
    def _extract_day_prayers(self, data, day, month, date_text, location):
        """
        Extracts and validates prayer times for a specific day.
        """
        day_prayers = data[month][day]
        if len(day_prayers) < 6:
            logger.error(f"Invalid prayer data for {location.upper()} on {date_text}: {day_prayers}")
            return {"error": f"Invalid prayer data for {location.upper()} on {date_text}"}
        return day_prayers

    # Find the next prayer time
    def _find_next_prayer(self, current_time, day_prayers_times):
        """
        Finds the next prayer time for the current day, considering the prayer switches.
        """
        logger.debug("Finding the next prayer for the current day.")
        next_prayer = None
        next_prayer_time = None

        for prayer, time_str in day_prayers_times.items():
            try:
                prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                    year=current_time.year, month=current_time.month, day=current_time.day, tzinfo=self._get_timezone()
                )
            except ValueError as e:
                logger.error(f"Invalid time format for prayer {prayer}: {time_str}. Error: {e}")
                continue

            logger.debug(f"Checking prayer {prayer} at {prayer_time}.")
            if prayer_time > current_time:
                if next_prayer_time is None or prayer_time < next_prayer_time:
                    next_prayer = prayer
                    next_prayer_time = prayer_time
                    logger.debug(f"Next prayer updated to {prayer} at {prayer_time}.")

        if next_prayer:
            logger.info(f"Next prayer is {next_prayer} at {next_prayer_time}.")
            return {"prayer": next_prayer, "prayer_time": next_prayer_time.strftime("%Y-%m-%d %H:%M:%S %z")}
        logger.info("No future prayers found for the current day.")
        return None

    # Find the first prayer for the next day
    def _find_first_prayer(self, next_day_date, next_day_prayers_times):
        """
        Finds the first prayer time for the next day, considering the prayer switches.
        """
        azan_switches = json.loads(os.getenv("AZAN_SWITCHES"))     # JSON string for prayer switches
        logger.debug("Finding the first prayer for the next day.")
        first_prayer = None
        first_prayer_time = None

        for prayer, time_str in next_day_prayers_times.items():
            if azan_switches.get(prayer, "Off") == "Off":
                logger.debug(f"Skipping prayer {prayer} as it is turned Off in the switches.")
                continue

            prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                year=next_day_date.year, month=next_day_date.month, day=next_day_date.day, tzinfo=self._get_timezone()
            )
            logger.debug(f"Checking prayer {prayer} at {prayer_time}.")
            if first_prayer_time is None or prayer_time < first_prayer_time:
                first_prayer = prayer
                first_prayer_time = prayer_time
                logger.debug(f"First prayer updated to {prayer} at {prayer_time}.")

        if first_prayer:
            logger.info(f"First prayer for the next day is {first_prayer} at {first_prayer_time}.")
            return {"prayer": first_prayer, "prayer_time": first_prayer_time.strftime("%Y-%m-%d %H:%M:%S %z")}
        logger.warning("No prayers found for the next day.")
        return None

    # Extract the next prayer time
    def _extract_next_prayer(self, data, location: str):
        """
        Extracts the next prayer time from the provided timetable data.
        """
        today_date = datetime.now(self._get_timezone())
        today_date_text = today_date.strftime("%Y-%m-%d")
        today_day = str(today_date.day)
        today_month = str(today_date.month)

        logger.debug(f"Extracting prayer times for {location.upper()} on {today_date_text}.")
        logger.info(f"Fetching prayer times for {location.upper()} on {today_date_text}.")
        day_prayers_times = self._get_day_prayers(data, today_day, today_month, today_date_text, location)
        if "error" in day_prayers_times:
            logger.error(f"Error fetching prayer times for {location.upper()} on {today_date_text}: {day_prayers_times['error']}.")
            return day_prayers_times
        logger.info(f"Prayer times for {location.upper()} on {today_date_text}: {day_prayers_times}.")
        
        logger.info(f"Finding the next prayer for {location.upper()} on {today_date_text}.")
        next_prayer = self._find_next_prayer(today_date, day_prayers_times)
        if next_prayer:
            logger.info(f"Next prayer for {location.upper()} on {today_date_text} is {next_prayer['prayer']} at {next_prayer['prayer_time']}.")
            return next_prayer

        logger.info(f"No future prayers found for {location.upper()} on {today_date_text}. Checking the next day.")
        next_day_date = today_date + timedelta(days=1)
        next_day_date_text = next_day_date.strftime("%Y-%m-%d")
        next_day = str(next_day_date.day)
        next_month = str(next_day_date.month)

        next_day_prayers_times = self._get_day_prayers(data, next_day, next_month, next_day_date_text, location)
        if "error" in next_day_prayers_times:
            logger.error(f"Error fetching prayer times for {location.upper()} on {next_day_date_text}: {next_day_prayers_times['error']}.")
            return next_day_prayers_times
        logger.info(f"Prayer times for {location.upper()} on {next_day_date_text}: {next_day_prayers_times}.")
        
        logger.info(f"Fetching the first prayer for {location.upper()} on {next_day_date_text}.")
        return self._find_first_prayer(next_day_date, next_day_prayers_times)

    # Check if the current month is a new month
    def _is_new_month(self, data):
        """
        Checks if the current month is a new month compared to the timetable data.
        """
        today_month = str(datetime.now(self._get_timezone()).month)
        if today_month not in data:
            logger.info("It is a new month. Timetable needs to be refreshed.")
            return True
        return False

    # Fetch today's prayer times
    def fetch_prayer_times(self, location):
        """
        Fetches today's prayer times for the specified location.
        Refreshes the timetable if it is a new month, if the data is missing, or if the file is outdated.
        """
        # Dynamically construct the timetable file path
        timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), f"{location}_formatted_timetable.json")

        # Parse the SOURCES environment variable as a dictionary
        sources = list(json.loads(os.getenv("SOURCES")).keys())  # Extract the keys as a list

        if location not in sources:
            logger.error(f"Invalid location provided: {location}. Available locations: {sources}")
            raise ValueError(f"Invalid location. Available locations: {sources}")

        if self._is_file_outdated(location):
            logger.info(f"The timetable file for {location.upper()} is outdated. Refreshing it.")
            if not self._refresh_timetable(location):
                return {"error": f"Failed to load or refresh {location.upper()} timetable."}

        data = self._reload_data(location)
        if not data or self._is_new_month(data):
            logger.info(f"Refreshing timetable for {location.upper()} due to new month or missing data.")
            if not self._refresh_timetable(location):
                return {"error": f"Failed to load or refresh {location.upper()} timetable."}
            data = self._reload_data(location)

        return self._extract_next_prayer(data, location)

# Example usage
if __name__ == "__main__":
    fetcher = PrayerTimesFetcher()

    naas_prayers = fetcher.fetch_prayer_times("naas")
    print(json.dumps(naas_prayers, indent=4))

    icci_prayers = fetcher.fetch_prayer_times("icci")
    print(json.dumps(icci_prayers, indent=4))
