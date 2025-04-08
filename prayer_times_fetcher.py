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

# Load environment variables from .env file
load_dotenv()

# Configure logging with debug level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
        Downloads the timetable for the specified location ('icci' or 'naas').
        """
        sources_url = {
            "icci": os.getenv("ICCI_API_URL"),
            "naas": os.getenv("NAAS_WEB_URL")
        }   # API URLs for ICCI and Naas
        icci_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("ICCI_TIMETABLE_FILE"))  # ICCI timetable file path
        naas_prayers_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("NAAS_TIMETABLE_FILE"))  # Naas timetable file path

        logging.debug(f"Attempting to download {location.upper()} timetable.")
        try:
            if location == "icci":
                response = requests.get(sources_url['icci'], timeout=10)
                response.raise_for_status()
                data = response.json()
                file_path = icci_timetable_file
            elif location == "naas":
                response = requests.get(sources_url['naas'], timeout=10)
                response.raise_for_status()
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
                    logging.error(f"❌ Calendar data not found in Naas webpage.")
                    return False
                data = json.loads(calendar_data)
                file_path = naas_prayers_timetable_file
            else:
                logging.error(f"Invalid location: {location}")
                return False

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            logging.info(f"✅ {location.upper()} timetable downloaded and saved successfully.")
            return True
        except (requests.RequestException, json.JSONDecodeError) as e:
            logging.error(f"❌ Failed to download {location.upper()} timetable: {e}.")
            return False

    # Refresh the timetable for Location
    def _refresh_timetable(self, location):
        """
        Refreshes the timetable for the specified location.
        """
        return self._download_timetable(location)

    # Reload the timetable data from the file
    def _reload_data(self, location):
        """
        Reloads the timetable data from the file for the specified location.
        """
        icci_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("ICCI_TIMETABLE_FILE"))  # ICCI timetable file path
        naas_prayers_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("NAAS_TIMETABLE_FILE"))  # Naas timetable file path

        file_path = icci_timetable_file if location == "icci" else naas_prayers_timetable_file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading {location.upper()} timetable: {e}.")
            return None

    # Wait until midnight
    def _wait_until_midnight(self):
        """
        Sleeps until midnight.
        """
        now = datetime.now(self._get_timezone())
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (midnight - now).total_seconds()
        logging.info(f"Sleeping for {seconds_until_midnight} seconds until midnight.")
        time.sleep(seconds_until_midnight)

    # Get prayer times for a specific day
    def _get_day_prayers(self, data, day, month, date_text, location):
        """
        Fetches prayer times for a specific day and month from the timetable data.
        If the day is missing, attempts to refresh the timetable once.
        If still missing, waits until the end of the day to retry refreshing.
        """
        if "timetable" not in data or month not in data["timetable"] or day not in data["timetable"][month]:
            logging.warning(f"{location.upper()} data missing for {date_text}. Attempting to refresh the timetable.")
            if not self._refresh_timetable(location):
                self._wait_until_midnight()
                if not self._refresh_timetable(location):
                    logging.error(f"{location.upper()} data for {date_text} is still missing after retry. Giving up.")
                    return {"error": f"{location.upper()} data missing for {date_text}. Please check the timetable source."}
            data = self._reload_data(location)
            if not data or "timetable" not in data or month not in data["timetable"] or day not in data["timetable"][month]:
                logging.error(f"{location.upper()} data for {date_text} is still missing after retry. Giving up.")
                return {"error": f"{location.upper()} data missing for {date_text}. Please check the timetable source."}
        return self._extract_day_prayers(data, day, month, date_text, location)

    # Extract prayer times for a specific day
    def _extract_day_prayers(self, data, day, month, date_text, location):
        """
        Extracts and validates prayer times for a specific day.
        """
        day_prayers = data["timetable"][month][day]
        if len(day_prayers) < 6:
            logging.error(f"Invalid prayer data for {location.upper()} on {date_text}: {day_prayers}")
            return {"error": f"Invalid prayer data for {location.upper()} on {date_text}"}
        return {
            "Fajr": f"{day_prayers[0][0]:02}:{day_prayers[0][1]:02}",
            "Sunrise": f"{day_prayers[1][0]:02}:{day_prayers[1][1]:02}",
            "Dhuhr": f"{day_prayers[2][0]:02}:{day_prayers[2][1]:02}",
            "Asr": f"{day_prayers[3][0]:02}:{day_prayers[3][1]:02}",
            "Maghrib": f"{day_prayers[4][0]:02}:{day_prayers[4][1]:02}",
            "Isha": f"{day_prayers[5][0]:02}:{day_prayers[5][1]:02}"
        }

    # Find the next prayer time
    def _find_next_prayer(self, current_time, day_prayers_times):
        """
        Finds the next prayer time for the current day, considering the prayer switches.
        """
        logging.debug("Finding the next prayer for the current day.")
        next_prayer = None
        next_prayer_time = None

        for prayer, time_str in day_prayers_times.items():
            # Skip prayers that are disabled in the switches
            try:
                prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                    year=current_time.year, month=current_time.month, day=current_time.day, tzinfo=self._get_timezone()
                )
            except ValueError as e:
                logging.error(f"Invalid time format for prayer {prayer}: {time_str}. Error: {e}")
                continue

            logging.debug(f"Checking prayer {prayer} at {prayer_time}.")
            if prayer_time > current_time:
                if next_prayer_time is None or prayer_time < next_prayer_time:
                    next_prayer = prayer
                    next_prayer_time = prayer_time
                    logging.debug(f"Next prayer updated to {prayer} at {prayer_time}.")

        if next_prayer:
            logging.info(f"Next prayer is {next_prayer} at {next_prayer_time}.")
            return {"prayer": next_prayer, "prayer_time": next_prayer_time.strftime("%Y-%m-%d %H:%M:%S %z")}
        logging.info("No future prayers found for the current day.")
        return None

    # Find the first prayer time for the next day
    def _find_first_prayer(self, next_day_date, next_day_prayers_times):
        """
        Finds the first prayer time for the next day, considering the prayer switches.
        """
        azan_switches = json.loads(os.getenv("AZAN_SWITCHES"))     # JSON string for prayer switches
        logging.debug("Finding the first prayer for the next day.")
        first_prayer = None
        first_prayer_time = None

        for prayer, time_str in next_day_prayers_times.items():
            # Skip prayers that are disabled in the switches
            if azan_switches.get(prayer, "Off") == "Off":
                logging.debug(f"Skipping prayer {prayer} as it is turned Off in the switches.")
                continue

            prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                year=next_day_date.year, month=next_day_date.month, day=next_day_date.day, tzinfo=self._get_timezone()
            )
            logging.debug(f"Checking prayer {prayer} at {prayer_time}.")
            if first_prayer_time is None or prayer_time < first_prayer_time:
                first_prayer = prayer
                first_prayer_time = prayer_time
                logging.debug(f"First prayer updated to {prayer} at {prayer_time}.")

        if first_prayer:
            logging.info(f"First prayer for the next day is {first_prayer} at {first_prayer_time}.")
            return {"prayer": first_prayer, "prayer_time": first_prayer_time.strftime("%Y-%m-%d %H:%M:%S %z")}
        logging.warning("No prayers found for the next day.")
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

        logging.debug(f"Extracting prayer times for {location.upper()} on {today_date_text}.")

        if location == "icci":
            # Validate and fetch today's prayer data
            logging.info(f"Fetching prayer times for {location.upper()} on {today_date_text}.")
            day_prayers_times = self._get_day_prayers(data, today_day, today_month, today_date_text, location)
            if "error" in day_prayers_times:
                logging.error(f"Error fetching prayer times for {location.upper()} on {today_date_text}: {day_prayers_times['error']}.")
                return day_prayers_times
            logging.info(f"Prayer times for {location.upper()} on {today_date_text}: {day_prayers_times}.")
            
            # Find the next prayer for today
            logging.info(f"Finding the next prayer for {location.upper()} on {today_date_text}.")
            next_prayer = self._find_next_prayer(today_date, day_prayers_times)
            if next_prayer:
                logging.info(f"Next prayer for {location.upper()} on {today_date_text} is {next_prayer['prayer']} at {next_prayer['prayer_time']}.")
                return next_prayer

            # If no future prayers are found, check the next day
            logging.info(f"No future prayers found for {location.upper()} on {today_date_text}. Checking the next day.")
            next_day_date = today_date + timedelta(days=1)
            next_day_date_text = next_day_date.strftime("%Y-%m-%d")
            next_day = str(next_day_date.day)
            next_month = str(next_day_date.month)

            next_day_prayers_times = self._get_day_prayers(data, next_day, next_month, next_day_date_text, location)
            if "error" in next_day_prayers_times:
                logging.error(f"Error fetching prayer times for {location.upper()} on {next_day_date_text}: {next_day_prayers_times['error']}.")
                return next_day_prayers_times
            logging.info(f"Prayer times for {location.upper()} on {next_day_date_text}: {next_day_prayers_times}.")
            
            # Return the first prayer of the next day
            logging.info(f"Fetching the first prayer for {location.upper()} on {next_day_date_text}.")
            return self._find_first_prayer(next_day_date, next_day_prayers_times)

        elif location == "naas":
            logging.info(f"Fetching prayer times for {location.upper()}.")
            # Similar logic for Naas can be implemented here if needed
            logging.error("Naas prayer data handling for next day is not implemented.")
            return {"error": "Naas prayer data handling for next day is not implemented."}

    # Check if the current month is new
    def _is_new_month(self, data):
        """
        Checks if the current month is a new month compared to the timetable data.
        """
        today_month = str(datetime.now(self._get_timezone()).month)
        if "timetable" not in data or today_month not in data["timetable"]:
            logging.info("It is a new month. Timetable needs to be refreshed.")
            return True
        return False

    # Check if the file is outdated
    def _is_file_outdated(self, file_path):
        """
        Checks if the file's creation or last modification date is in the current month
        or the last day of the previous month.
        """
        try:
            # Get the file's last modification time
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=self._get_timezone())
            today = datetime.now(self._get_timezone())
            last_day_of_previous_month = today.replace(day=1)  + timedelta(days=1)
  
            # Check if the file was modified in the current month or on the last day of the previous month
            if file_mod_time >= last_day_of_previous_month:
                return False  # File is up-to-date
            return True  # File is outdated
        except FileNotFoundError:
            logging.warning(f"File {file_path} not found. It will be treated as outdated.")
            return True  # Treat missing file as outdated

    # Fetch prayer times for a specific location
    def fetch_prayer_times(self, location):
        """
        Fetches today's prayer times for the specified location ('naas' or 'icci').
        Refreshes the timetable if it is a new month, if the data is missing, or if the file is outdated.
        """
        icci_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("ICCI_TIMETABLE_FILE"))  # ICCI timetable file path
        naas_prayers_timetable_file = os.path.join(os.getenv("CONFIG_FOLDER"), os.getenv("NAAS_TIMETABLE_FILE"))  # Naas timetable file path

        if location not in {"naas", "icci"}:
            logging.error(f"Invalid location provided: {location}.")
            raise ValueError("Invalid location. Choose either 'naas' or 'icci'.")

        file_path = icci_timetable_file if location == "icci" else naas_prayers_timetable_file

        # Check if the file is outdated
        if self._is_file_outdated(file_path):
            logging.info(f"The timetable file for {location.upper()} is outdated. Refreshing it.")
            if not self._refresh_timetable(location):
                return {"error": f"Failed to load or refresh {location.upper()} timetable."}

        # Reload data from the file
        data = self._reload_data(location)
        if not data or self._is_new_month(data):
            logging.info(f"Refreshing timetable for {location.upper()} due to new month or missing data.")
            if not self._refresh_timetable(location):
                return {"error": f"Failed to load or refresh {location.upper()} timetable."}
            data = self._reload_data(location)

        return self._extract_next_prayer(data, location)
    
# Example usage
if __name__ == "__main__":
    fetcher = PrayerTimesFetcher()

    # Fetch prayer times for Naas
    naas_prayers = fetcher.fetch_prayer_times("naas")
    print(json.dumps(naas_prayers, indent=4))

    # Fetch prayer times for ICCI
    icci_prayers = fetcher.fetch_prayer_times("icci")
    print(json.dumps(icci_prayers, indent=4))
