import pyatv
import asyncio
import logging
from pyatv.const import Protocol
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def cast_music_to_homepod():
    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Discover Apple TV devices on the network
    atvs = await pyatv.scan(loop, identifier="024203835863")
    if not atvs:
        logging.error("❌ HomePod is not detected on the network")
        return

    homepod = atvs[0]
    logging.info(f"✅ HomePod online - Name: {homepod.name} - IP:{homepod.address}")

    # Connect to the first discovered device
    atv = await pyatv.connect(homepod, loop)
    try:
        # Set the volume to 50% before streaming
        await atv.audio.set_volume(50.0)
        logging.info(f"🔊 Volume set to 50% on {homepod.name}")

        # Play a music file on the device
        file_path = os.path.join(os.getcwd(), 'media', 'Short_Azan.mp3')
        logging.info(f"🎵 Playing file: {file_path}")
        await atv.stream.stream_file(file_path)

        logging.info(f"✅ File is done playing on {homepod.name} - IP:{homepod.address}")
    finally:
        # Disconnect from the device
        atv.close()  # No need to await this call

# Run the asyncio event loop
asyncio.run(cast_music_to_homepod())