from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from apple_manager import AppleManager
from config_update import ConfigUpdater
from azan_scheduler import AzanScheduler
from logging_config import get_logger  # Import the centralized logger

# Get a logger for this module
logger = get_logger(__name__)


# Create a FastAPI app instance
app = FastAPI()

# Initialize the AppleManager,ConfigUpdater and AzanScheduler
manager = AppleManager()
config_updater = ConfigUpdater()
scheduler = AzanScheduler()

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
    try:
        # Call the update_env_keys method with the received updates
        logger.info(f"Received update request: {request.updates}")
        update_status = config_updater.update_env_keys(request.updates)

        # Return the status of the updates
        return {"status": "success", "update_status": update_status}
    except Exception as e:
        logger.error(f"❌ Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration.")


@app.post("/api/restart-scheduler")
def restart_scheduler():
    """
    Restart the Azan scheduler.
    """
    try:
        scheduler.run()
        return {"message": "Azan scheduler restarted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart scheduler: {e}")

