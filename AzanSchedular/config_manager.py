import sys
import os
import shutil
import json
import re
from dateutil import tz
import aiofiles
from AzanSchedular.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)


class SystemConfigManager:
    def __init__(self):
        self.config_dir_path = os.path.join(os.getcwd(), 'config')
        self.system_file_path = os.path.join(self.config_dir_path, 'system.json')
        self.ensure_system_config()
        self.system_config = self.load_sys_config_file()

    def ensure_system_config(self):
        """
        Ensures the config folder and system.json exist in the current working directory.
        If not, copies them from the PyInstaller _MEIPASS directory.
        """

        if hasattr(sys, '_MEIPASS'):
            source_config_dir = os.path.join(sys._MEIPASS, 'config')
            source_system_file = os.path.join(source_config_dir, 'system.json')

            # If config directory doesn't exist, copy the entire directory
            if not os.path.exists(self.config_dir_path):
                try:
                    shutil.copytree(
                        source_config_dir,
                        self.config_dir_path
                    )
                    logger.info("✅ Config folder has been recreated by SystemConfigManager.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate config folder: {e}")
                    raise
            # If system.json file is missing, copy only the file
            elif not os.path.exists(self.system_file_path):
                try:
                    shutil.copy2(source_system_file, self.system_file_path)
                    logger.info("✅ system.json file has been recreated.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate system.json file: {e}")
                    raise
        else:
            if not os.path.exists(self.config_dir_path) or not os.path.exists(self.system_file_path):
                logger.error("❌ Config folder or system.json missing and can't be recreated.")
                raise FileNotFoundError("Config folder or system.json missing and can't be recreated.")

    def load_sys_config_file(self):
        """
        Loads the configuration from the system.json file.
        """
        with open(self.system_file_path, "r") as f:
            system_config = json.load(f)
        return system_config

    def load_sys_config(self, key):
        """
        Loads a specific key from the system configuration.
        """
        return self.system_config.get(key, None)


class ConfigManager:
    def __init__(self):
        self.config_dir_path = os.path.join(os.getcwd(), 'config')
        self.config_file_path = os.path.join(self.config_dir_path, 'config.json')
        self.default_timetable_file_path = os.path.join(self.config_dir_path, 'default_formatted_timetable.json')
        self.media_folder = os.path.join(os.getcwd(), 'media')
        self.ensure_config_folder()


    def ensure_config_folder(self):
        """
        Ensures the config folder, config.json and default_formatted_timetable.json exist in the current working directory.
        If not, copies them from the PyInstaller _MEIPASS directory.
        """

        if hasattr(sys, '_MEIPASS'):
            source_config_dir = os.path.join(sys._MEIPASS, 'config')
            source_config_file = os.path.join(source_config_dir, 'config.json')
            source_default_timetable_file = os.path.join(source_config_dir, 'default_formatted_timetable.json')

            # If config directory doesn't exist, copy the entire directory
            if not os.path.exists(self.config_dir_path):
                try:
                    shutil.copytree(
                        source_config_dir,
                        self.config_dir_path
                    )
                    logger.info("✅ Config folder has been recreated by ConfigManager.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate config folder: {e}")
                    raise
            # If config.json file is missing, copy only the file
            if not os.path.exists(self.config_file_path):
                try:
                    shutil.copy2(source_config_file, self.config_file_path)
                    logger.info("✅ config.json file has been recreated.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate config.json file: {e}")
                    raise
            # If default_formatted_timetable.json file is missing, copy only the file
            if not os.path.exists(self.default_timetable_file_path):
                try:
                    shutil.copy2(source_default_timetable_file, self.default_timetable_file_path)
                    logger.info("✅ default_formatted_timetable.json file has been recreated.")
                except Exception as e:
                    logger.error(f"❌ Failed to recreate default_formatted_timetable.json file: {e}")
                    raise
        else:
            if not os.path.exists(self.config_dir_path) or not os.path.exists(self.config_file_path) or not os.path.exists(self.default_timetable_file_path):
                logger.error("❌ Config folder or config.json or default_formatted_timetable.json missing and can't be recreated.")
                raise FileNotFoundError("Config folder or config.json or default_formatted_timetable.json missing and can't be recreated.")

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

    def _sanitize_sources(self, value: dict) -> dict:
        """
        Normalizes the value is a dictionary for sources.:
        - Ensures it's a dict
        - Ensures 'default' exists and is '--'
        - Removes invalid URLs for non-default sources
        Returns a NEW cleaned dict.
        """
        status_messages = []
        if not isinstance(value, dict):
            logger.error(f"❌ Key 'SOURCES' must be a dictionary with source names as keys and valid URLs as values.")
            status_messages.append( f"Key 'SOURCES' must be a dictionary with source names as keys and valid URLs as values.")
            return {}, status_messages

        cleaned = dict(value)  # shallow copy

        # Ensure default exists and is correct
        if cleaned.get("default") != "--":
            cleaned["default"] = "--"

        # Remove invalid URLs (except default)
        invalid_sources = []
        for name, url in cleaned.items():
            if name == "default":
                continue
            if not self._validate_url(url):
                logger.error(f"❌ Invalid URL for source '{name}': {url}")
                status_messages.append( f"Invalid URL for source '{name}'.")
                invalid_sources.append(name)

        for name in invalid_sources:
            del cleaned[name]

        return cleaned,status_messages

    def _is_validate_key(self, key: str, type=None) -> bool:
        if type == "audio":
            allowed_keys = ["REGULAR_AZAN_FILE", "FAJR_AZAN_FILE", "SHORT_AZAN_FILE", "DUAA_FILE"]
        else:
            allowed_keys = ["SOURCES", "DEFAULT_TIMETABLE", "TIMEZONE", "AZAN_SWITCHES", "SHORT_AZAN_SWITCHES", "DUAA_SWITCHES", "ISHA_GAMA_SWITCH", "AUDIO_VOLUME", "DEVICES"]
        return key in allowed_keys

    async def update_env_keys(self, updates: dict) -> dict:
        """
        Updates multiple keys in the config.json file with the given values and returns a status for each key.
        """
        status = {}
        required_prayer_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
        config = self.load_config()

        for key, value in updates.items():
            if not self._is_validate_key(key):
                logger.error(f"❌ '{key}' is not a valid config key.")
                return {"status": "fail", "message": f"'{key}' is not a valid config key."}

            # Validate SOURCES as a dictionary
            if key == "SOURCES":
                cleaned_sources,status_messages = self._sanitize_sources(value)
                if not cleaned_sources:
                    logger.error("❌ SOURCES must be a dictionary with at least the 'default' source.")
                    status[key] = {"status": "fail", "message": ", ".join(status_messages)}
                    continue
                value = cleaned_sources

            # Validate DEFAULT_TIMETABLE to be a valid source key
            if key == "DEFAULT_TIMETABLE":
                if "SOURCES" in updates:
                    candidate_sources, status_messages = self._sanitize_sources(updates["SOURCES"])
                else:
                    candidate_sources = config.get("SOURCES", {})

                sources = list(candidate_sources.keys())

                if value not in sources:
                    logger.error(f"❌ Key '{key}' must be one of the available sources: {sources}.")
                    status[key] = {"status": "fail","message": f"Key '{key}' must be one of the available sources: {sources}."}
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
                from AzanSchedular.scheduler_manager import restart_scheduler
                await restart_scheduler()
                status[key] = {"status": "updated", "message": f"Key '{key}' updated successfully."}
            except Exception as e:
                logger.error(f"❌ Failed to update key '{key}': {e}")
                status[key] = {"status": "fail", "message": f"Failed to update key '{key}': {e}"}

        return status

    async def update_media_file(self, file_name: str, audio_file: str, file_bytes):
        """
        Updates a file in the media folder and updates the config.json with the new file name.

        Args:
            file_name (str): The name of the file to save in the media folder.
            audio_file (str): The config key to update (e.g., FAJR_AZAN_FILE).
            file_bytes (bytes): The binary content of the file.
        """
        try:
            if not self._is_validate_key(audio_file, "audio"):
                logger.error(f"❌ '{audio_file}' is not a valid audio file key.")
                return {"status": "fail", "message": f"'{audio_file}' is not a valid audio file key."}

            # Replace spaces with underscores in file name
            file_name = file_name.replace(" ", "_")

            # Check for duplicate file name in other audio keys
            config = self.load_config()
            audio_keys = ["REGULAR_AZAN_FILE", "FAJR_AZAN_FILE", "SHORT_AZAN_FILE", "DUAA_FILE"]
            for key in audio_keys:
                if key != audio_file and config.get(key) == file_name:
                    logger.error(f"❌ File name '{file_name}' is already assigned to '{key}'.")
                    return {
                        "status": "fail",
                        "message": f"File name '{file_name}' is already assigned to '{key}'. Please use a different file name."
                    }

            # Ensure the media folder exists
            if not os.path.exists(self.media_folder):
                os.makedirs(self.media_folder)

            # Save the file
            file_path = os.path.join(self.media_folder, file_name)
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(file_bytes)
            logger.info(f"✅ Saved media file: {file_name}")

            # Update config.json directly
            config = self.load_config()
            config[audio_file] = file_name
            self.save_config(config)
            logger.info(f"✅ Updated {audio_file} in config.json file to: {file_name}")
            return {"status": "success", "message": f"{audio_file} updated to {file_name}"}

        except Exception as e:
            logger.error(f"❌ Failed to update media file {file_name}: {e}")
            return {"status": "fail", "message": str(e)}

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

    def load_default_timetable(self):
        """
        Loads the Timtable from the default_formatted_timetable.json file.
        """
        with open(self.default_timetable_file_path, "r") as f:
            data = json.load(f)
        return data
