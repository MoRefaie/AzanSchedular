from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
from scheduler_manager import start_scheduler, stop_scheduler, scheduler_status  # Import scheduler functions
from apple_manager import AppleManager
from config_manager import ConfigManager, SystemConfigManager  # Import the configuration manager
from prayer_times_fetcher import PrayerTimesFetcher
from logging_config import get_logger  # Import the centralized logger

# Get a logger for this module
logger = get_logger(__name__)

# Initialize the AppleManager,ConfigManager and AzanScheduler
apple_manager = AppleManager()
config = ConfigManager()
sys_config = SystemConfigManager()
cors_config = sys_config.load_sys_config("API_CORS") or {}
prayer_fetcher = PrayerTimesFetcher()


# Create a FastAPI app instance
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", ["*"]),
    allow_credentials=cors_config.get("allow_credentials", True),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)

class ConfigManagerGetRequest(BaseModel):
    list: list  # A dictionary of keys and values to update in the .env file

class ConfigManagerUpdateRequest(BaseModel):
    updates: dict  # A dictionary of keys and values to update in the .env file

@app.get("/api/prayer-times")
async def prayer_times():
    """
    Fetches today's prayer times using PrayerTimesFetcher.
    Returns:
        JSon: A dictionary containing the prayer times for the day or an error message.
    """
    logger.info("Received request to /prayer-times endpoint.")
    try:
        # Call the scan_for_devices method
        logger.info("Get today's prayer time.")
        today_prayer_times = prayer_fetcher.fetch_prayer_times("today")
        logger.info(f"Today's prayer times Results: {today_prayer_times}")
        return {"status": "success", "data": today_prayer_times}
    
    except Exception as e:
        logger.error(f"An error occurred while geting today's prayer times: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/scan-devices")
async def scan_devices():
    """
    API endpoint to scan for Apple TV devices on the network.
    Returns:
        JSON: The result of the scan_for_devices method.
    """
    logger.info("Received request to /scan-devices endpoint.")
    try:
        # Call the scan_for_devices method
        logger.info("Starting device scan...")
        devices_json = await apple_manager.scan_for_devices()
        logger.info("Device scan completed successfully.")
        logger.info(f"Scan Results: {devices_json}")
        return {"status": "success", "data": devices_json}
    except Exception as e:
        logger.error(f"An error occurred while scanning for devices: {e}")
        return {"status": "error", "message": str(e)}
    
@app.post("/api/get-config")
async def get_config(request: ConfigManagerGetRequest):
    """
    API endpoint to get configuration values from the .env file.
    Args:
        request (ConfigManagerGetRequest): The request object containing the keys to retrieve.
    Returns:
        JSON: A dictionary containing the configuration values for the specified keys.
    """
    logger.info("Received request to api/get-config endpoint.")
    try:
        # Call the get_config_values method with the received keys
        logger.info(f"Received request to get config values for keys: {request.list}")
        config_values = config.get_config_values(request.list)
        logger.info(f"Config values retrieved successfully: {config_values}")
        return {"status": "success", "data": config_values}
    
    except Exception as e:
        logger.error(f"An error occurred while getting config values: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/update-config")
async def update_config(request: ConfigManagerUpdateRequest):
    """
    API endpoint to update configuration keys in the .env file.
    """
    logger.info("Received request to /update-config endpoint.")
    try:
        # Call the update_env_keys method with the received updates
        logger.info(f"Received update request: {request.updates}")
        update_status = await config.update_env_keys(request.updates)

        # Return the status of the updates
        return {"status": "success", "update_status": update_status}
    except Exception as e:
        logger.error(f"❌ Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration.")
    
@app.post("/api/update-audio")
async def update_audio(file: UploadFile = File(...), fileType: str = Form(...)):
    """
    API endpoint to update a media file.
    Expects a multipart/form-data request with an audio file and a fileType.
    """
    logger.info("Received request to /update-media-file endpoint.")
    try:
        # Check if the uploaded file is an audio file
        if not file.content_type.startswith("audio/"):
            logger.error(f"Uploaded file is not an audio file: {file.content_type}")
            raise HTTPException(status_code=400, detail="Uploaded file must be an audio file.")

        file_bytes = await file.read()
        file_name = file.filename

        logger.info(f"Updating media file: {file_name}, fileType: {fileType}")

        # Pass the file name, fileType, and binary data to config_manager
        update_status = await config.update_media_file(file_name, fileType, file_bytes)

        return {"status": "success", "update_status": update_status}
    except Exception as e:
        logger.error(f"❌ Failed to update media file: {e}")
        raise HTTPException(status_code=500, detail="Failed to update media file.")

@app.get("/api/scheduler-status")
async def api_scheduler_status():
    """
    API endpoint to get the Azan scheduler status.
    Args:
        api_call (bool): Indicates whether the function was called via an API request.
    """
    logger.info("Received request to /scheduler-status endpoint.")
    try:
        # Call the scheduler_status method
        return await scheduler_status()
    except Exception as e:
        logger.error(f"❌ Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {e}")

@app.post("/api/start-scheduler")
async def api_start_scheduler():
    """
    API endpoint to start the Azan scheduler.
    Args:
        api_call (bool): Indicates whether the function was called via an API request.
    """
    logger.info("Received request to /start-scheduler endpoint.")
    try:
        # Call the start_scheduler method
        return await start_scheduler()
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {e}")


@app.post("/api/stop-scheduler")
async def api_stop_scheduler():
    """
    API endpoint to stop the Azan scheduler.
    Args:
        api_call (bool): Indicates whether the function was called via an API request.
    """
    logger.info("Received request to /stop-scheduler endpoint.")
    try:
        # Call the stop_scheduler method
        return await stop_scheduler()
    except Exception as e:
        logger.error(f"❌ Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {e}")
