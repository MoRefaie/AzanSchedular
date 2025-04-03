import pyatv
import asyncio
import logging
from pyatv.const import Protocol
import io

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AppleManager:
    async def _discover_device(self, loop, identifier):
        """
        Discovers an Apple device on the network by its identifier.
        """
        logging.info(f"🔍 Discovering device with identifier: {identifier}")
        atvs = await pyatv.scan(loop, identifier=identifier)
        if not atvs:
            logging.error(f"❌ Device with identifier {identifier} not found on the network.")
            return None
        logging.info(f"✅ Device found - Name: {atvs[0].name} - IP: {atvs[0].address}")
        return atvs[0]

    async def _play_file(self, loop, device, file_path):
        """
        Connects to the device and plays the specified file.
        """
        logging.info(f"🎵 Connecting to device: {device.name} - IP: {device.address}")
        atv = await pyatv.connect(device, loop)
        try:
            logging.info(f"✅ File is now playing on {device.name} - IP: {device.address}")
            with io.open(file_path, "rb") as audio_file:
                await atv.stream.stream_file(audio_file)
            logging.info(f"✅ File is done playing on {device.name} - IP: {device.address}")
        finally:
            atv.close()

    async def announce(self, file_path, device_identifiers):
        """
        Announces a file on the specified devices.

        Args:
            file_path (str): The path of the file to play.
            device_identifiers (list): A list of device identifiers to announce on.
        """
        tasks = []
        for identifier in device_identifiers:
            loop = asyncio.get_event_loop()
            device = await self._discover_device(loop,identifier)
            if device:
                tasks.append(self._play_file(loop, device, file_path))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            logging.error("❌ No devices were found to announce on.")


# Example usage:
if __name__ == "__main__":
    manager = AppleManager()
    file_to_play = "C:\\Dev\\IEPrayer\\media\\Fajr_Azan.mp3"
    devices = ["024203835863", "123456789012"]  # Replace with actual device identifiers
    asyncio.run(manager.announce(file_to_play, devices))