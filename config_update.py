import os
import shutil
import logging
from dotenv import load_dotenv, set_key
import json
import re
from dateutil import tz

class ConfigUpdater:
    def __init__(self, env_file_path=".env", media_folder="media"):
        """
        Initializes the ConfigUpdater class.

        Args:
            env_file_path (str): Path to the .env file.
            media_folder (str): Path to the media folder.
        """
        self.env_file_path = os.path.join(os.getcwd(), env_file_path)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        # Load environment variables from the .env file
        load_dotenv()

    def _validate_url(self, value):
        """
        Validates if the value is a valid URL.
        """
        url_regex = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'([a-zA-Z0-9.-]+)'  # domain
            r'(\.[a-zA-Z]{2,})'  # top-level domain
            r'(:\d+)?(/.*)?$'  # optional port and path
        )
        return bool(url_regex.match(value))

    def _validate_dict(self, value, required_keys):
        """
        Validates if the value is a dictionary with the required keys and values being "On" or "Off".
        """
        if not isinstance(value, dict):
            return False
        for key in required_keys:
            if key not in value or value[key] not in ["On", "Off"]:
                return False
        return True

    def update_env_keys(self, updates: dict) -> dict:
        """
        Updates multiple keys in the .env file with the given values and returns a status for each key.

        Args:
            updates (dict): A dictionary where keys are the environment variable names
                            and values are the new values to set.

        Returns:
            dict: A dictionary where keys are the environment variable names and values are their update status:
                  - "updated": Successfully updated.
                  - "not_exist": Key does not exist in the environment variables.
                  - "fail": Failed to update the key.
        """
        status = {}
        required_prayer_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for key, value in updates.items():
            # Block updates to specific keys
            if key in ["REGULAR_AZAN_FILE", "FAJR_AZAN_FILE", "SHORT_AZAN_FILE"]:
                logging.error(f"❌ Key '{key}' cannot be updated. It is managed elsewhere.")
                status[key] = {"status": "blocked", "message": f"Key '{key}' cannot be updated."}
                continue

            # Validate ICCI_API_URL and NAAS_WEB_URL as URLs
            if key in ["ICCI_API_URL", "NAAS_WEB_URL"]:
                if not self._validate_url(value):
                    logging.error(f"❌ Key '{key}' must be a valid URL.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a valid URL."}
                    continue

            # Validate DEFAULT_TIMETABLE to be "icci" or "nass"
            if key == "DEFAULT_TIMETABLE":
                if value not in ["icci", "nass"]:
                    logging.error(f"❌ Key '{key}' must be 'icci' or 'nass'.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be 'icci' or 'nass'."}
                    continue

            # Validate TIMEZONE to be a valid timezone using dateutil.tz
            if key == "TIMEZONE":
                try:
                    # Attempt to get the timezone using dateutil.tz
                    if tz.gettz(value) is None:
                        raise ValueError
                except ValueError:
                    logging.error(f"❌ Key '{key}' must be a valid timezone.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a valid timezone."}
                    continue

            # Validate ICCI_TIMETABLE_FILE and NAAS_TIMETABLE_FILE to be .json files
            if key in ["ICCI_TIMETABLE_FILE", "NAAS_TIMETABLE_FILE"]:
                if not value.endswith(".json"):
                    logging.error(f"❌ Key '{key}' must be a .json file.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a .json file."}
                    continue

            # Validate AZAN_SWITCHES and SHORT_AZAN_SWITCHES to be valid dictionaries
            if key in ["AZAN_SWITCHES", "SHORT_AZAN_SWITCHES"]:
                if not self._validate_dict(value, required_prayer_keys):
                    logging.error(f"❌ Key '{key}' must be a dictionary with keys {required_prayer_keys} and values 'On' or 'Off'.")
                    status[key] = {
                        "status": "fail",
                        "message": f"Key '{key}' must be a dictionary with keys {required_prayer_keys} and values 'On' or 'Off'."
                    }
                    continue

            # Validate AUDIO_VOLUME to be a float between 0.0 and 1.0
            if key == "AUDIO_VOLUME":
                try:
                    volume = float(value)
                    if not (0.0 <= volume <= 1.0):
                        raise ValueError
                except ValueError:
                    logging.error(f"❌ Key '{key}' must be a float between 0.0 and 1.0.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a float between 0.0 and 1.0."}
                    continue

            # Ensure DEVICES is always a list
            if key == "DEVICES":
                if not isinstance(value, list):
                    value = [value]

            try:
                # Convert value to a JSON string if it's a list or dict
                value = json.dumps(value) if isinstance(value, (list, dict)) else f'"{value}"'

                # Update the key in the .env file
                set_key(self.env_file_path, key, value, quote_mode="never")

                # Reload the environment variable
                os.environ[key] = value.strip('"')
                logging.info(f"✅ Updated {key} in .env file to: {value}")
                status[key] = {"status": "updated", "message": f"Key '{key}' updated successfully."}
            except Exception as e:
                logging.error(f"❌ Failed to update key '{key}': {e}")
                status[key] = {"status": "fail", "message": f"Failed to update key '{key}': {e}"}

        return status

    def update_media_file(self, file_name: str, new_file_path: str):
        """
        Updates a file in the media folder and backs up the existing one.

        Args:
            file_name (str): The name of the file to update in the media folder.
            new_file_path (str): The path to the new file to replace the existing one.
        """
        media_folder = os.getenv("MEDIA_FOLDER", media_folder)
        try:
            # Ensure the media folder exists
            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            # Path to the existing file in the media folder
            existing_file_path = os.path.join(media_folder, file_name)

            # Backup the existing file if it exists
            if os.path.exists(existing_file_path):
                backup_file_path = f"{existing_file_path}.backup"
                shutil.move(existing_file_path, backup_file_path)
                logging.info(f"🔄 Backed up existing file to: {backup_file_path}")

            # Move the new file to the media folder
            shutil.move(new_file_path, existing_file_path)
            logging.info(f"✅ Updated media file: {file_name}")
        except Exception as e:
            logging.error(f"❌ Failed to update media file {file_name}: {e}")

