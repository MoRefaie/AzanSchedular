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

# Load environment variables from .env file
load_dotenv()

# Configure logging with debug level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PrayerTimesFetcher:
    def __init__(self):
        """
        Initializes the prayer time fetcher with sources, file paths, timezone settings, and prayer switches.
        """
        self.sources = {
            "icci": os.getenv("ICCI_API_URL"),
            "naas": os.getenv("NAAS_WEB_URL")
        }
        self.naas_prayers_timetable_file = os.getenv("NAAS_TIMETABLE_FILE")
        self.icci_timetable_file = os.getenv("ICCI_TIMETABLE_FILE")
        self.tz = tz.gettz(os.getenv("TIMEZONE"))

        # Load prayer switches from the .env file
        prayer_switches_json = os.getenv("PRAYER_SWITCHES")
        self.prayer_switches = json.loads(prayer_switches_json)

        if self.tz is None:
            raise ValueError("Timezone could not be initialized. Check your timezone configuration.")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _download_icci_timetable(self):
        """
        Fetches and saves the ICCI prayer timetable from the API.
        """
        logging.debug("Attempting to download ICCI timetable.")
        try:
            response = requests.get(self.sources['icci'], timeout=10)
            response.raise_for_status()  # Raise error if response is not successful
            with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(self.icci_timetable_file)) as temp_file:
                json.dump(response.json(), temp_file, indent=4)
                temp_filename = temp_file.name
            os.replace(temp_filename, self.icci_timetable_file)
            logging.info("✅ ICCI timetable downloaded and saved successfully.")
            return True
        except requests.RequestException as e:
            logging.error(f"❌ Failed to download ICCI timetable: {e}.")
            return False
    
    def _download_naas_timetable(self):
        """
        Fetches prayer timetable data for Naas using web scraping.
        Extracts 'calendar' data from the webpage and saves it to a JSON file.
        """
        logging.debug("Attempting to download Naas timetable from Mawaqit.")
        try:
            response = requests.get(self.sources['naas'], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            script_tags = soup.find_all("script")

            calendar_data = None
            for script in script_tags:
                if "calendar" in script.text:
                    match = re.search(r'"calendar"\s*:\s*(\[\{.*?\}\])', script.text, re.DOTALL)
                    if match:
                        calendar_data = match.group(1)
                    break  # Stop searching once we find the calendar data
            
            if not calendar_data:
                logging.error(f"❌ Calendar data not found in Naas webpage. Response snippet: {response.text[:500]}")
                return False

            calendar_list = json.loads(calendar_data)
            with open(self.naas_prayers_timetable_file, "w", encoding="utf-8") as file:
                json.dump(calendar_list, file, indent=2, ensure_ascii=False)

            logging.info("✅ Naas prayer timetable saved successfully.")
            return True
        except requests.RequestException as e:
            logging.error(f"❌ Error fetching Naas data: {e}.")
            return False
        except json.JSONDecodeError as e:
            logging.error(f"❌ Error parsing Naas JSON: {e}.")
            return False

    def _is_new_month(self):
        """
        Determines if the timetable should be refreshed by checking if a new month has started.
        Also, checks if timetable files exist.
        """
        logging.debug("Checking if a new month has started or timetable files are missing.")
        if not os.path.exists(self.icci_timetable_file) or not os.path.exists(self.naas_prayers_timetable_file):
            logging.info("One or both timetable files are missing. Need to download new ones.")
            return True  # Need to download a new timetable

        try:
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(self.icci_timetable_file))
            current_month = datetime.today().month
            current_month_text = datetime.today().strftime("%B %Y")
            is_new_month = file_mod_time.month != current_month
            logging.debug(f"Timetable last modified in month: {file_mod_time.month}, Current month: {current_month_text}.")
            return is_new_month
        except Exception as e:
            logging.error(f"Error reading timetable file modification date for {self.icci_timetable_file}: {e}.")
            return True  # If any error occurs, assume we need to re-download

    def fetch_prayer_times(self, location: str = 'icci'):
        """
        Fetches today's prayer times for the specified location ('naas' or 'icci').
        If it's a new month, it downloads a fresh timetable.
        """
        if location not in {"naas", "icci"}:
            logging.error(f"Invalid location provided: {location}.")
            raise ValueError("Invalid location. Choose either 'naas' or 'icci'.")

        if self._is_new_month():
            logging.info("New month detected. Downloading updated timetables.")
            if not self._download_icci_timetable() or not self._download_naas_timetable():
                return {"error": "Failed to download prayer timetable."}

        filename = self.icci_timetable_file if location == "icci" else self.naas_prayers_timetable_file
        if not os.path.exists(filename):
            logging.error(f"{location.upper()} timetable file not found.")
            return {"error": f"{location.upper()} timetable file not found."}

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._extract_next_prayer(data, location)
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Error loading {location.upper()} timetable: {e}.")
            return {"error": f"Failed to load {location.upper()} timetable."}


    def _extract_next_prayer(self, data, location: str):
        """
        Extracts the next prayer time from the provided timetable data.
        """
        today_date = datetime.now(self.tz)
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

    # Helper function to validate and fetch prayer times for a specific day
    def _get_day_prayers(self, data, day, month, date_text, location):
        """
        Fetches prayer times for a specific day and month from the timetable data.
        """
        logging.debug(f"Fetching prayer times for {location.upper()} on {date_text}.")
        if "timetable" not in data or month not in data["timetable"] or day not in data["timetable"][month]:
            logging.warning(f"{location.upper()} data missing for {date_text}.")
            return {"error": f"{location.upper()} data missing for {date_text}"}

        day_prayers = data["timetable"][month][day]
        if len(day_prayers) < 6:
            logging.error(f"Invalid prayer data for {location.upper()} on {date_text}: {day_prayers}")
            return {"error": f"Invalid prayer data for {location.upper()} on {date_text}"}
        logging.debug(f"Prayer times for {location.upper()} on {date_text}: {day_prayers}.")
        return {
            "Fajr": f"{day_prayers[0][0]:02}:{day_prayers[0][1]:02}",
            "Sunrise": f"{day_prayers[1][0]:02}:{day_prayers[1][1]:02}",
            "Dhuhr": f"{day_prayers[2][0]:02}:{day_prayers[2][1]:02}",
            "Asr": f"{day_prayers[3][0]:02}:{day_prayers[3][1]:02}",
            "Maghrib": f"{day_prayers[4][0]:02}:{day_prayers[4][1]:02}",
            "Isha": f"{day_prayers[5][0]:02}:{day_prayers[5][1]:02}"
        }

    # Helper function to find the next prayer for a given day
    def _find_next_prayer(self, current_time, day_prayers_times):
        """
        Finds the next prayer time for the current day, considering the prayer switches.
        """
        logging.debug("Finding the next prayer for the current day.")
        next_prayer = None
        next_prayer_time = None

        for prayer, time_str in day_prayers_times.items():
            # Skip prayers that are disabled in the switches
            if self.prayer_switches.get(prayer, "Off") == "Off":
                logging.debug(f"Skipping prayer {prayer} as it is turned Off in the switches.")
                continue

            try:
                prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                    year=current_time.year, month=current_time.month, day=current_time.day, tzinfo=self.tz
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
            return {"prayer": next_prayer, "prayer_time": next_prayer_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")}
        logging.info("No future prayers found for the current day.")
        return None

    # Helper function to find the first prayer for the next day
    def _find_first_prayer(self, next_day_date, next_day_prayers_times):
        """
        Finds the first prayer time for the next day, considering the prayer switches.
        """
        logging.debug("Finding the first prayer for the next day.")
        first_prayer = None
        first_prayer_time = None

        for prayer, time_str in next_day_prayers_times.items():
            # Skip prayers that are disabled in the switches
            if self.prayer_switches.get(prayer, "Off") == "Off":
                logging.debug(f"Skipping prayer {prayer} as it is turned Off in the switches.")
                continue

            prayer_time = datetime.strptime(time_str, "%H:%M").replace(
                year=next_day_date.year, month=next_day_date.month, day=next_day_date.day, tzinfo=self.tz
            )
            logging.debug(f"Checking prayer {prayer} at {prayer_time}.")
            if first_prayer_time is None or prayer_time < first_prayer_time:
                first_prayer = prayer
                first_prayer_time = prayer_time
                logging.debug(f"First prayer updated to {prayer} at {prayer_time}.")

        if first_prayer:
            logging.info(f"First prayer for the next day is {first_prayer} at {first_prayer_time}.")
            return {"prayer": first_prayer, "prayer_time": first_prayer_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")}
        logging.warning("No prayers found for the next day.")
        return None
    
# Example usage
if __name__ == "__main__":
    fetcher = PrayerTimesFetcher()

    # Fetch prayer times for Naas
    naas_prayers = fetcher.fetch_prayer_times("naas")
    print(json.dumps(naas_prayers, indent=4))

    # Fetch prayer times for ICCI
    icci_prayers = fetcher.fetch_prayer_times("icci")
    print(json.dumps(icci_prayers, indent=4))
