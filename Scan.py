import pyatv
import asyncio
import logging
from tabulate import tabulate

# Configure logging with debug level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def scan_for_devices():
    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Discover Apple TV devices on the network
    atvs = await pyatv.scan(loop)

    # Filter out devices from the discovered devices
    devices = [atv for atv in atvs]

    if not devices:
        logging.error("❌ No Apple devices found on the network")
    else:
        logging.info("✅ Found the following Apple devices:")
        table_data = [[idx + 1, str(device)] for idx, device in enumerate(devices)]
        table_headers = ["#", "Device Info"]
        
        # Log the table
        logging.info("\n" + tabulate(table_data, headers=table_headers, tablefmt="grid"))

# Run the asyncio event loop
asyncio.run(scan_for_devices())