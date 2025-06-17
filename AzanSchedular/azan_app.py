import sys
import os
import asyncio
import uvicorn
import threading
import pystray
from PIL import Image
import webbrowser
import subprocess
from AzanSchedular.api import app
from AzanSchedular.scheduler_manager import start_scheduler
from AzanSchedular.logging_config import get_logger
from AzanSchedular.config_manager import ConfigManager, SystemConfigManager

# Get a logger for this module
logger = get_logger(__name__)

# Get the configuration manager instances
config = ConfigManager()
sys_config = SystemConfigManager()

if hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    media_dir = os.path.join(sys._MEIPASS, 'media')
else:
    # Running in normal Python environment
    media_dir = os.path.join(os.getcwd(), 'media')

shutdown_trigger = False


async def shutdown():
    """
    Cleans up tasks, stops the event loop, and logs the shutdown process.
    """
    logger.info("Shutting down application...")

    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logger.info(f"Canceling {len(tasks)} running tasks...")
    [task.cancel() for task in tasks]

    # Wait for all tasks to finish
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All tasks canceled.")

    # Stop the event loop
    loop = asyncio.get_event_loop()
    if not loop.is_closed():
        loop.stop()
        logger.info("Event loop stopped.")

    logger.info("Shutdown process completed.")


async def start_api():
    """
    Starts the FastAPI application using uvicorn and logs its output asynchronously.
    """
    logger.info("Starting the API...")
    config = uvicorn.Config(app, host=sys_config.load_sys_config("API_HOST"), port=sys_config.load_sys_config("API_PORT"), log_level="info", log_config=None, lifespan="on")
    server = uvicorn.Server(config)

    try:
        # Run Uvicorn in the background
        server_task = asyncio.create_task(server.serve())
        logger.info("API process started. Waiting for it to be ready...")

        # Check if the server is running
        while not server.started:  # Wait until Uvicorn reports it has started
            await asyncio.sleep(0.1)  # Prevent busy waiting

        if server.started:
            logger.info("✅ API started successfully.")
            return server, server_task
        else:
            logger.error("❌ Failed to start API.")
            return None, None

    except BaseException:
        # Catch BaseException explicitly and log the error
        logger.error("❌ Failed to start API.")
        return None, None

    except Exception as e:
        # Catch other exceptions and log them
        logger.error("❌ Failed to start API.")
        logger.error(f"Exception: {e}")
        return None, None


# Ensure event loop runs properly

async def start_web():
    """
    Starts the AzanUI application and logs its output asynchronously.
    """
    logger.info("Starting the AzanUI...")
    azanui_path = os.path.join(os.getcwd(), sys_config.load_sys_config("UI_APP"))
    if not os.path.exists(azanui_path):
        logger.info(f"AzanUI file not found at {azanui_path}. Assuming AzanUI is started (file missing).")
        return "AzanUI_MISSING"
    try:
        # Hide the CMD window on Windows
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        # Run the Node.js application as an asynchronous subprocess
        process = await asyncio.create_subprocess_exec(
            azanui_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=creationflags
        )
        logger.info("AzanUI process started. Waiting for it to be ready...")
        async for line in process.stdout:
            decoded_line = line.decode().strip()
            if decoded_line != "":
                logger.info(f"AzanUI: {decoded_line}")
                if "Server running" in decoded_line:
                    logger.info("✅ AzanUI is ready.")
                    return process  # Return the process object
        logger.error("❌ Failed to start AzanUI.")
        return None
    except FileNotFoundError as e:
        logger.error(f"❌ Failed to start AzanUI: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred while starting AzanUI: {e}")
        return None


async def main():
    """
    Runs the API application, the AzanUI, and the AzanScheduler sequentially.
    """
    logger.info("Starting the API, AzanUI, and AzanScheduler sequentially...")

    azanui_server = None
    try:
        # Start the API and wait for it to be ready
        api_server, api_task = await start_api()
        if api_task is None:
            logger.error("❌ API start error, Exiting...")
        else:
            # Start the AzanUI and wait for it to be ready
            azanui_server = await start_web()
            if azanui_server is None:
                logger.error("❌ AzanUi start error, Exiting...")
            else:
                if azanui_server == "AzanUI_MISSING":
                    logger.error("❌ AzanUI file is missing.")
                else:
                    logger.info("✅ AzanUI started successfully.")

                # Start the AzanScheduler and wait for it
                await start_scheduler()

                # Open the UI in the default web browser
                ui_url = sys_config.load_sys_config("UI_URL")
                if ui_url and azanui_server != "AzanUI_MISSING":
                    logger.info(f"Opening AzanUI in browser: {ui_url}")
                    webbrowser.open(ui_url)

                while not shutdown_trigger:
                    await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Gracefully shutdown Uvicorn
        if api_server:
            logger.info("Signaling Uvicorn server to shut down gracefully...")
            api_server.should_exit = True
            await api_task  # Wait for Uvicorn to finish gracefully
        # Terminate AzanUI process if running
        if azanui_server and azanui_server.returncode is None:
            logger.info("Terminating AzanUI process...")
            azanui_server.terminate()
            await azanui_server.wait()
        # Call the shutdown function
        await shutdown()


def on_quit(icon, item):
    global shutdown_trigger
    icon.stop()
    shutdown_trigger = True


def on_open_azanui(icon, item):
    webbrowser.open(sys_config.load_sys_config("UI_URL"))


def setup_tray_icon():
    # Use your icon file path here
    icon_path = os.path.join(media_dir, "icon.ico")
    image = Image.open(icon_path)
    menu = pystray.Menu(
        pystray.MenuItem('Open AzanUI', on_open_azanui),
        pystray.MenuItem('Quit', on_quit)
    )
    icon = pystray.Icon("AzanSchedular", image, "Azan Schedular", menu)
    icon.run()


if __name__ == "__main__":
    # Start tray icon in a separate thread so it doesn't block your main app
    tray_thread = threading.Thread(target=setup_tray_icon, daemon=True)
    tray_thread.start()
    try:
        asyncio.run(main())
    except SystemExit:
        pass
    except BaseException:
        pass
    except RuntimeError as e:
        logger.error(f"RuntimeError occurred: {e}")
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
    finally:
        logger.info("Shutting down completed.")
