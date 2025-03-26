import pyatv
import asyncio

async def scan_for_devices():
    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Discover Apple TV devices on the network
    atvs = await pyatv.scan(loop)

    # Filter out devices from the discovered devices
    devices = [atv for atv in atvs]

    if not devices:
        print("No Apple devices found on the network.")
    else:
        print("Found the following Apple devices:")
        for device in devices:
            print(f"- Name: {device.name} - IP:{device.address}")
            print(device)
            print("============================================")

# Run the asyncio event loop
asyncio.run(scan_for_devices())