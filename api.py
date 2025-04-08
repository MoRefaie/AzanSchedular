from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from apple_manager import AppleManager
from config_update import ConfigUpdater

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a FastAPI app instance
app = FastAPI()

# Initialize the AppleManager
manager = AppleManager()

# Initialize the ConfigUpdater
config_updater = ConfigUpdater()

class ConfigUpdateRequest(BaseModel):
    updates: dict  # A dictionary of keys and values to update in the .env file

@app.get("/scan-devices")
async def scan_devices():
    """
    API endpoint to scan for Apple TV devices on the network.
    Returns:
        JSON: The result of the scan_for_devices method.
    """
    logging.info("Received request to /scan-devices endpoint.")
    try:
        # Call the scan_for_devices method
        logging.info("Starting device scan...")
        devices_json = await manager.scan_for_devices()
        logging.info("Device scan completed successfully.")
        logging.info(f"Scan Results: {devices_json}")
        return {"status": "success", "data": devices_json}
    except Exception as e:
        logging.error(f"An error occurred while scanning for devices: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/update-config")
async def update_config(request: ConfigUpdateRequest):
    """
    API endpoint to update configuration keys in the .env file.
    """
    try:
        # Call the update_env_keys method with the received updates
        logging.info(f"Received update request: {request.updates}")
        update_status = config_updater.update_env_keys(request.updates)

        # Return the status of the updates
        return {"status": "success", "update_status": update_status}
    except Exception as e:
        logging.error(f"❌ Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration.")