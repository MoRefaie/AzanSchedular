import asyncio
from apple_manager import AppleManager

async def test_scan_for_devices():
    """
    Test function to call scan_for_devices and display the result.
    """
    manager = AppleManager()
    try:
        # Call the scan_for_devices method
        devices_json = await manager.scan_for_devices()

        # Print the result
        print("Scan Results:")
        print(devices_json)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Use asyncio.run to properly manage the event loop
    asyncio.run(test_scan_for_devices())