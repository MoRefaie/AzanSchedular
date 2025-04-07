import pyatv
import asyncio
import logging
from pyatv.const import Protocol
from tabulate import tabulate
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

    async def scan_for_devices(self):
        """
        Scans for Apple TV devices on the network and returns the results.

        Returns:
            str: A Dict containing the list of discovered devices.
        """
        # Get the current event loop
        loop = asyncio.get_event_loop()

        # Discover Apple TV devices on the network
        atvs = await pyatv.scan(loop)

        # Extract attributes for each discovered device
        devices = []
        for atv in atvs:
            services = []
            for service in atv.services:
                # Convert each service to a dictionary
                service_info = {
                    "protocol": str(service.protocol).replace("Protocol.", ""),  # Remove "Protocol."
                    "port": service.port,
                    "credentials": service.credentials,
                    "requires_password": service.requires_password,
                    "password": service.password,
                    "pairing": str(service.pairing).replace("PairingRequirement.", ""),  # Remove "PairingRequirement."
                }
                services.append(service_info)
            device_info = {
                "name": atv.name,
                "address": str(atv.address),
                "mac": atv.identifier,
                "identifier": atv.all_identifiers[1] if len(atv.all_identifiers) > 1 else atv.all_identifiers[0],
                "deep_sleep": atv.deep_sleep,
                "device_info": str(atv.device_info),
                "ready": atv.ready,
                "services": services
            }
            devices.append(device_info)

        if not devices:
            logging.error("❌ No Apple devices found on the network.")
            return {"status": "error", "message": "No Apple devices found on the network."}
        else:
            logging.info("✅ Found the following Apple devices:")

            # Define table headers
            table_headers = [
                "#", "Device Name", "IP Address", "MAC Identifier", "Identifier", "Deep Sleep",
                "Device Info", "Ready", "Services"
            ]

            # Prepare table data
            table_data = [
                [
                    idx + 1,
                    device["name"],
                    device["address"],
                    device["mac"],
                    device["identifier"],
                    device["deep_sleep"],
                    device["device_info"],
                    device["ready"],
                    device["services"],
                ]
                for idx, device in enumerate(devices)
            ]

            # Log the table
            logging.info("\n" + tabulate(table_data, headers=table_headers, tablefmt="grid"))

            # Return the devices as dict
            return {"status": "success", "devices": devices}

# Example usage:
if __name__ == "__main__":
    manager = AppleManager()
    file_to_play = "C:\\Dev\\IEPrayer\\media\\Fajr_Azan.mp3"
    devices = ["024203835863", "123456789012"]  # Replace with actual device identifiers
    asyncio.run(manager.announce(file_to_play, devices))
    devices = asyncio.run(manager.scan_for_devices())
