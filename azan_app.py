import asyncio
import logging
import uvicorn
from api import app  # Import the API app
from azan_scheduler import AzanScheduler  # Import the AzanScheduler class

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start_api():
    """
    Starts the API application using uvicorn and logs its output asynchronously.
    """
    logging.info("Starting the API...")
    try:
        # Run the API application as an asynchronous subprocess
        process = await asyncio.create_subprocess_shell(
            "uvicorn api:app --host 127.0.0.1 --port 8000 --log-level info",  # Command to start the API app
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Log the stdout and stderr in real-time
        logging.info("API process started. Waiting for it to be ready...")
        async for line in process.stdout:
            decoded_line = line.decode().strip()
            logging.info(f"API: {decoded_line}")
            # Check for a specific line indicating the API is ready
            if "Uvicorn running on" in decoded_line:
                logging.info("API is ready.")
                break
        # Wait for the process to complete (optional, if you want to keep it running)
        if process.returncode == 0:
            logging.info("API process completed successfully.")
        else:
            logging.error(f"API process exited with code {process.returncode}.")
    except FileNotFoundError as e:
        logging.error(f"Failed to start API: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while starting API: {e}")

async def start_web():
    """
    Starts the AzanUI application and logs its output asynchronously.
    """
    logging.info("Starting the AzanUI...")
    try:
        # Run the Node.js application as an asynchronous subprocess
        process = await asyncio.create_subprocess_shell(
            "npm start",  # Command to start the Node.js app
            cwd="AzanUI",  # Path to the AzanUI directory
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        logging.info("API process started. Waiting for it to be ready...")
        async for line in process.stdout:
            decoded_line = line.decode().strip()
            if decoded_line != "":
                logging.info(f"AzanUI: {decoded_line}")
                # Check for a specific line indicating the API is ready
                if "Network" in decoded_line:
                    logging.info("AzanUI is ready.")
                    break
    except FileNotFoundError as e:
        logging.error(f"Failed to start AzanUI: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while starting AzanUI: {e}")

async def main():
    """
    Runs the API application, the AzanUI, and the AzanScheduler sequentially.
    """
    logging.info("Starting the API, AzanUI, and AzanScheduler sequentially...")

    # Create an instance of AzanScheduler
    scheduler = AzanScheduler()

    try:
        # Start the API and wait for it to be ready
        await start_api()
        logging.info("API started successfully.")

        # Start the AzanUI and wait for it to be ready
        await start_web()
        logging.info("AzanUI started successfully.")

        # Start the AzanScheduler
        await scheduler.run()
        logging.info("AzanScheduler started successfully.")

    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        asyncio.get_event_loop().stop()

if __name__ == "__main__":
    try:
        # Run the main function in the asyncio event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Application interrupted by user.")
    except RuntimeError as e:
        logging.error(f"RuntimeError occurred: {e}")