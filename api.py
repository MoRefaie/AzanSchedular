from fastapi import FastAPI
import asyncio
from apple_manager import AppleManager

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
    try:
        # Call the scan_for_devices method
        devices_json = await manager.scan_for_devices()
        return {"status": "success", "data": devices_json}
    except Exception as e:
        return {"status": "error", "message": str(e)}