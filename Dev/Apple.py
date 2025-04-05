import pyatv
import asyncio
from pyatv.const import Protocol

async def cast_music_to_homepod():
    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Discover Apple TV devices on the network
    atvs = await pyatv.scan(loop,identifier="223344556677")
    homepod = atvs[0]
    print(f"- Name: {homepod.name} - IP:{homepod.address}")

    if not atvs:
        print("HomePod is not detected on the network.")
        return

    # Connect to the first discovered device
    atv = await pyatv.connect(homepod,loop)
    try:
        # Play a music URL on the device
        await atv.stream.stream_file("https://www.gurutux.com/media/Athan.mp3")
        print("Music is now playing on the Apple HomePod.")
    finally:
        # Disconnect from the device
        atv.close()  # No need to await this call

# Run the asyncio event loop
asyncio.run(cast_music_to_homepod())