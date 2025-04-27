import asyncio
import logging
import uvicorn
from api import app  # Import the FastAPI app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - API: %(message)s")

# Define custom log formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - API: %(message)s", datefmt="%Y-%m-%d %H:%M:%S,%f")

# Capture Uvicorn logs and format them
uvicorn_logger = logging.getLogger("uvicorn")
for handler in uvicorn_logger.handlers:
    handler.setFormatter(formatter)

# Add a custom log handler to capture Uvicorn logs separately
class UvicornLogHandler(logging.Handler):
    def emit(self, record):
        log_message = formatter.format(record)
        logging.getLogger("custom_uvicorn").info(log_message)

# Attach the custom handler
uvicorn_logger.addHandler(UvicornLogHandler())

async def start_api():
    """
    Starts the FastAPI application using Uvicorn in the background.
    """
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info", access_log=True)
    server = uvicorn.Server(config)

    # Run Uvicorn in the background
    server_task = asyncio.create_task(server.serve())

    # Monitor logs and detect when the API starts
    await monitor_uvicorn_logs(server)
    return server_task

async def monitor_uvicorn_logs(server):
    """
    Monitors Uvicorn logs and detects when the server is running.
    """
    while not server.started:  # Wait until Uvicorn reports it has started
        await asyncio.sleep(0.1)  # Prevent busy waiting
    
    logging.info("API started successfully.")

async def main():
    """
    Starts the API while ensuring logging runs after startup.
    """
    server_task = await start_api()  # Start API in background
    logging.info("API startup confirmed.")
    print("API started test.")  # Print final message
    
    # Keep the process running cleanly
    await server_task  

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
