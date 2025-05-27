import sys
import os
import shutil
import logging
import json
import re
from dateutil import tz
import asyncio
from logging_config import get_logger  # Import the centralized logger

# Get a logger for this module
logger = get_logger(__name__)

class ConfigManager:
    def __init__(self, media_folder="media"):
        self.config_dir_path = os.path.join(os.getcwd(), 'config')
        self.config_file_path = os.path.join(self.config_dir_path, 'config.json')
        self.media_folder = media_folder
        self.ensure_config_folder()

    def ensure_config_folder(self):
        """
        Ensures the config folder and config.json exist in the current working directory.
        If not, copies them from the PyInstaller _MEIPASS directory.
        """

        if hasattr(sys, '_MEIPASS'):
            source_config_dir = os.path.join(sys._MEIPASS, 'config')
            source_config_file = os.path.join(source_config_dir, 'config.json')

            # If config directory doesn't exist, copy the entire directory
            if not os.path.exists(self.config_dir_path):
                try:
                    shutil.copytree(source_config_dir, self.config_dir_path)
                    logger.info(f"✅ Config folder has been recreated.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate config folder: {e}")
                    raise
            # If config.json file is missing, copy only the file
            elif not os.path.exists(self.config_file_path):
                try:
                    shutil.copy2(source_config_file, self.config_file_path)
                    logger.info(f"✅ config.json file has been recreated.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate config.json file: {e}")
                    raise
        else:
            if not os.path.exists(self.config_dir_path) or not os.path.exists(self.config_file_path):
                logger.error("❌ Config folder or config.json missing and can't be recreated.")
                raise FileNotFoundError("Config folder or config.json missing and can't be recreated.")

    def load_config(self, key=None):
        """
        Loads the configuration from the config.json file.
        If a key is provided, returns the value for that key.
        If no key is provided, returns the entire config dictionary.
        """
        with open(self.config_file_path, "r") as f:
            config = json.load(f)
        if key:
            return config.get(key)
        return config

    def save_config(self, config):
        with open(self.config_file_path, "w") as f:
            json.dump(config, f, indent=4)

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

    def _validate_dict_switch(self, value, required_keys):
        """
        Validates if the value is a dictionary with the required keys and values being "On" or "Off".
        """
        if not isinstance(value, dict):
            return False
        for key in required_keys:
            if key not in value or value[key] not in ["On", "Off"]:
                return False
        return True

    def _validate_single_switch(self, value):
        """
        Validates if the value being "On" or "Off".
        """
        if not isinstance(value, str):
            return False
        if value not in ["On", "Off"]:
            return False
        return True

    def _validate_dict_source(self, value):
        """
        Validates if the value is a dictionary for sources.
        """
        if not isinstance(value, dict):
            return False
        for url in value.values():
            if not self._validate_url(url):
                print(f"Invalid URL: {url}")
                return False
        return True

    async def update_env_keys(self, updates: dict) -> dict:
        """
        Updates multiple keys in the config.json file with the given values and returns a status for each key.
        """
        status = {}
        required_prayer_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
        config = self.load_config()

        for key, value in updates.items():
            # Block updates to specific keys
            if key in ["REGULAR_AZAN_FILE", "FAJR_AZAN_FILE", "SHORT_AZAN_FILE"]:
                logger.error(f"❌ Key '{key}' cannot be updated. It is managed elsewhere.")
                status[key] = {"status": "blocked", "message": f"Key '{key}' cannot be updated."}
                continue

            # Validate SOURCES as a dictionary
            if key == "SOURCES":
                if not self._validate_dict_source(value):
                    logger.error(f"❌ Key '{key}' must be a dictionary where each key is a source name and each value is a valid URL.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a dictionary with source names as keys and valid URLs as values."}
                    continue

            # Validate DEFAULT_TIMETABLE to be a valid source key
            if key == "DEFAULT_TIMETABLE":
                if "SOURCES" in updates.keys() and self._validate_dict_source(updates["SOURCES"]):
                    sources = list(updates["SOURCES"].keys())
                else:
                    sources = list(config.get("SOURCES", {}).keys())
                if value not in sources:
                    logger.error(f"❌ Key '{key}' must be one of the available sources: {sources}.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be one of the available sources: {sources}."}
                    continue

            # Validate TIMEZONE to be a valid timezone using dateutil.tz
            if key == "TIMEZONE":
                try:
                    if tz.gettz(value) is None:
                        raise ValueError
                except ValueError:
                    logger.error(f"❌ Key '{key}' must be a valid timezone.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a valid timezone."}
                    continue

            # Validate AZAN_SWITCHES and SHORT_AZAN_SWITCHES to be valid dictionaries
            if key in ["AZAN_SWITCHES", "SHORT_AZAN_SWITCHES", "DUAA_SWITCHES"]:
                if not self._validate_dict_switch(value, required_prayer_keys):
                    logger.error(f"❌ Key '{key}' must be a dictionary with keys {required_prayer_keys} and values 'On' or 'Off'.")
                    status[key] = {
                        "status": "fail",
                        "message": f"Key '{key}' must be a dictionary with keys {required_prayer_keys} and values 'On' or 'Off'."
                    }
                    continue

            if key == "ISHA_GAMA_SWITCH":
                if not self._validate_single_switch(value):
                    logger.error(f"❌ Key '{key}' values must be 'On' or 'Off'.")
                    status[key] = {
                        "status": "fail",
                        "message": f"Key '{key}' values must be 'On' or 'Off'."
                    }
                    continue

            # Validate AUDIO_VOLUME to be a float between 0.0 and 100.0
            if key == "AUDIO_VOLUME":
                try:
                    volume = float(value)
                    if not (0.0 <= volume <= 100.0):
                        raise ValueError
                except ValueError:
                    logger.error(f"❌ Key '{key}' must be a float between 0.0 and 100.0.")
                    status[key] = {"status": "fail", "message": f"Key '{key}' must be a float between 0.0 and 100.0."}
                    continue

            # Ensure DEVICES is always a list
            if key == "DEVICES":
                if not isinstance(value, list):
                    value = [value]

            try:
                config[key] = value
                self.save_config(config)
                logger.info(f"✅ Updated {key} in config.json file to: {value}")
                # Move import here to avoid circular import
                from scheduler_manager import restart_scheduler
                await restart_scheduler()
                status[key] = {"status": "updated", "message": f"Key '{key}' updated successfully."}
            except Exception as e:
                logger.error(f"❌ Failed to update key '{key}': {e}")
                status[key] = {"status": "fail", "message": f"Failed to update key '{key}': {e}"}

        return status

    def update_media_file(self, file_name: str, new_file_path: str):
        """
        Updates a file in the media folder and backs up the existing one.

        Args:
            file_name (str): The name of the file to update in the media folder.
            new_file_path (str): The path to the new file to replace the existing one.
        """
        media_folder = self.media_folder
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
                logger.info(f"🔄 Backed up existing file to: {backup_file_path}")

            # Move the new file to the media folder
            shutil.move(new_file_path, existing_file_path)
            logger.info(f"✅ Updated media file: {file_name}")
        except Exception as e:
            logger.error(f"❌ Failed to update media file {file_name}: {e}")

    def get_config_values(self, keys: list) -> dict:
        """
        Retrieves the values for the specified keys from the config.json file.

        Args:
            keys (list): A list of keys to retrieve from the config.json file.

        Returns:
            dict: A dictionary containing the key-value pairs for the specified keys.
        """
        try:
            config = self.load_config()
            config_values = {}
            for key in keys:
                if key in config:
                    config_values[key] = config[key]
                else:
                    logger.warning(f"⚠️ Key '{key}' not found in the config.json file.")

            logger.info(f"✅ Successfully retrieved configuration values for keys: {keys}")
            return config_values
        except Exception as e:
            logger.error(f"❌ Failed to retrieve configuration values: {e}")
            return {"error": str(e)}

