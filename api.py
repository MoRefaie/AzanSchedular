from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from scheduler_manager import start_scheduler, stop_scheduler, restart_scheduler  # Import scheduler functions
from apple_manager import AppleManager
from config_update import ConfigUpdater
from logging_config import get_logger  # Import the centralized logger

# Get a logger for this module
logger = get_logger(__name__)


# Create a FastAPI app instance
app = FastAPI()

# Initialize the AppleManager,ConfigUpdater and AzanScheduler
manager = AppleManager()
config_updater = ConfigUpdater()

class ConfigUpdateRequest(BaseModel):
    updates: dict  # A dictionary of keys and values to update in the .env file

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
        devices_json = await manager.scan_for_devices()
        logger.info("Device scan completed successfully.")
        logger.info(f"Scan Results: {devices_json}")
        return {"status": "success", "data": devices_json}
    except Exception as e:
        logger.error(f"An error occurred while scanning for devices: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/update-config")
async def update_config(request: ConfigUpdateRequest):
    """
    API endpoint to update configuration keys in the .env file.
    """
    logger.info("Received request to /update-config endpoint.")
    try:
        # Call the update_env_keys method with the received updates
        logger.info(f"Received update request: {request.updates}")
        update_status = await config_updater.update_env_keys(request.updates)

        # Return the status of the updates
        return {"status": "success", "update_status": update_status}
    except Exception as e:
        logger.error(f"❌ Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration.")

@app.get("/api/restart-scheduler")
async def api_restart_scheduler():
    """
    API endpoint to restart the Azan scheduler.
    """
    logger.info("Received request to /restart-scheduler endpoint.")
    try:
        # Call the restart_scheduler method
        return await restart_scheduler()
    except Exception as e:
        logger.error(f"❌ Failed to restart scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart scheduler: {e}")

@app.get("/api/start-scheduler")
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


@app.get("/api/stop-scheduler")
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
