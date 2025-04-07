from fastapi import FastAPI
import asyncio
import logging
from apple_manager import AppleManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a FastAPI app instance
app = FastAPI()

# Initialize the AppleManager
manager = AppleManager()

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