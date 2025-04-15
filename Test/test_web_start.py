import os
import asyncio
import logging
from pynpm import NPMPackage



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def start_web():
    """
    Starts the AzanUI application and logs its output asynchronously.
    """
    logging.info("Starting the AzanUI...")
    logging.info(f"Working Directory: {os.path.join(os.getcwd(), 'AzanUI')}")

    if not os.path.exists(os.path.join(os.getcwd(), "AzanUI")):
        logging.error("AzanUI directory does not exist.")
        return
    
    logging.info("Checking if npm is available...")
    process = await asyncio.create_subprocess_shell(
        "npm --version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.error(f"npm Error: {stderr.decode().strip()}")
        return
    else:
        logging.info(f"npm Version: {stdout.decode().strip()}")

    # Run the Node.js application as an asynchronous subprocess
    process = await asyncio.create_subprocess_shell(
        "npm start",  # Command to start the Node.js app
        cwd=os.path.join(os.getcwd(), "AzanUI"),  # Path to the AzanUI directory
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Log the stdout and stderr in real-time
    async for line in process.stdout:
        logging.info(f"AzanUI: {line.decode().strip()}")
    async for line in process.stderr:
        logging.error(f"AzanUI Error: {line.decode().strip()}")

    # Wait for the process to complete
    await process.wait()
    logging.info("AzanUI process completed.")


def start_web_py():
    """
    Starts the AzanUI application and logs its output asynchronously.
    """
    try:
        logging.info("Starting the AzanUI...")

        # Get the working directory for AzanUI
        azanui_path = os.path.join(os.getcwd(), 'AzanUI', 'package.json')
        logging.info(f"Resolved AzanUI package.json path: {azanui_path}")

        # Check if the package.json file exists
        if not os.path.exists(azanui_path):
            logging.error(f"package.json not found at: {azanui_path}")
            return

        # Initialize the NPMPackage
        pkg = NPMPackage(azanui_path, shell=True)
        logging.info(f"Initialized NPMPackage with path: {azanui_path}")

        # Run the npm start script
        logging.info("Running npm start script...")
        pkg.run_script('start')
        logging.info("npm start script executed successfully.")

    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

async def main():
    """
    Runs the FastAPI application, the AzanScheduler, and the AzanUI concurrently.
    """
    logging.info("Starting the API, Azan Scheduler, and AzanUI...")

    # Run the API, AzanScheduler, and AzanUI concurrently
    await asyncio.gather(
        start_web()  # Start the AzanUI
    )


if __name__ == "__main__":
    try:
        # Run the main function in the asyncio event loop
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError occurred: {e}")



