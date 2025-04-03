import pyatv
import asyncio
import logging
from pyatv.const import Protocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def cast_music_to_homepod():
    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Discover Apple TV devices on the network
    atvs = await pyatv.scan(loop,identifier="024203835863")
    homepod = atvs[0]
    logging.info(f"✅ HomePod online - Name: {homepod.name} - IP:{homepod.address}")

    if not atvs:
        logging.error("❌ HomePod is not detected on the network")
        return

    # Connect to the first discovered device
    atv = await pyatv.connect(homepod,loop)
    try:
        logging.info(f"✅ File is now playing on {homepod.name} - IP:{homepod.address}")
        # Play a music URL on the device
        await atv.stream.stream_file("https://www.gurutux.com/media/Athan.mp3")
        logging.info(f"✅ File is done playing on {homepod.name} - IP:{homepod.address}")
    finally:
        # Disconnect from the device
        atv.close()  # No need to await this call

# Run the asyncio event loop
asyncio.run(cast_music_to_homepod())