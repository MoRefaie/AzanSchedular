import asyncio
import logging
import uvicorn
from api import app  # Import the FastAPI app
from azan_scheduler import AzanScheduler  # Import the AzanScheduler class

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start_api():
    """
    Starts the FastAPI application using uvicorn.
    """
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """
    Runs the FastAPI application and the AzanScheduler concurrently.
    """
    logging.info("Starting the API and Azan Scheduler...")

    # Create an instance of AzanScheduler
    scheduler = AzanScheduler()

    # Run the API and AzanScheduler concurrently
    await asyncio.gather(
        start_api(),  # Start the FastAPI server
        scheduler.run()  # Call the async run method of AzanScheduler
    )

if __name__ == "__main__":
    try:
        # Run the main function in the asyncio event loop
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError occurred: {e}")