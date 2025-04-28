import asyncio
import uvicorn
from api import app  # Import the API app
from scheduler_manager import start_scheduler  # Import the start_scheduler function
from logging_config import get_logger  # Import the centralized logger

# Get a logger for this module
logger = get_logger(__name__)

async def start_api():
    """
    Starts the FastAPI application using uvicorn and logs its output asynchronously.
    """
    logger.info("Starting the API...")
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info", lifespan="on")
    server = uvicorn.Server(config)

    try:
        # Run Uvicorn in the background
        server_task = asyncio.create_task(server.serve())
        logger.info("API process started. Waiting for it to be ready...")

        # Check if the server is running
        while not server.started:  # Wait until Uvicorn reports it has started
            await asyncio.sleep(0.1)  # Prevent busy waiting
        if server.started:
            logger.info("API started successfully.")
            return server_task
        else:
            logger.error("Failed to start API.")

    except Exception as e:
        logger.error(f"An unexpected error occurred while starting API: {e}")

async def start_web():
    """
    Starts the AzanUI application and logs its output asynchronously.
    """
    logger.info("Starting the AzanUI...")
    try:
        # Run the Node.js application as an asynchronous subprocess
        process = await asyncio.create_subprocess_shell(
            "npm start",  # Command to start the Node.js app
            cwd="AzanUI",  # Path to the AzanUI directory
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        logger.info("API process started. Waiting for it to be ready...")
        async for line in process.stdout:
            decoded_line = line.decode().strip()
            if decoded_line != "":
                logger.info(f"AzanUI: {decoded_line}")
                # Check for a specific line indicating the API is ready
                if "Network" in decoded_line:
                    logger.info("AzanUI is ready.")
                    break
    except FileNotFoundError as e:
        logger.error(f"Failed to start AzanUI: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while starting AzanUI: {e}")

async def main():
    """
    Runs the API application, the AzanUI, and the AzanScheduler sequentially.
    """
    logger.info("Starting the API, AzanUI, and AzanScheduler sequentially...")

    try:
        # Start the API and wait for it to be ready
        await start_api()

        # Start the AzanUI and wait for it to be ready
        # await start_web()
        logger.info("AzanUI started successfully.")

        # Start the AzanScheduler and wait for it
        await start_scheduler()

        while True:
            await asyncio.sleep(1) 

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
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
        logger.info("Application interrupted by user.")
    except RuntimeError as e:
        logger.error(f"RuntimeError occurred: {e}")