import asyncio
import logging
from azan_scheduler import AzanScheduler

# Get a logger for this module
logger = logging.getLogger(__name__)

# Global variable to track the scheduler task
scheduler_task = None
scheduler = AzanScheduler()  # Initialize the AzanScheduler

async def scheduler_status():
    """
    Returns the status of the Azan scheduler.

    Returns:
        dict: A dictionary containing the status and whether the scheduler is active.
    """
    global scheduler_task

    if scheduler_task and not scheduler_task.done():
        logger.info("Scheduler is active.")
        return {"status": "success", "data": {"active": True}}
    else:
        logger.info("Scheduler is not active.")
        return {"status": "success", "data": {"active": False}}
    
async def start_scheduler():
    """
    Starts the Azan scheduler.
    Args:
        task (bool): Indicates whether the function should return the scheduler task.
    """
    global scheduler_task

    if scheduler_task and not scheduler_task.done():
        logger.warning("Scheduler is already running.")
        return {"status": "error", "message": "Scheduler is already running."}

    try:
        logger.info("Creating a new scheduler task...")
        scheduler_task = asyncio.create_task(scheduler.run())
        logger.info("Azan scheduler started successfully.")
        return {"status": "success", "message": "Azan scheduler started successfully."}
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        return {"status": "error", "message": f"Failed to start scheduler: {e}"}


async def stop_scheduler():
    """
    Stops the Azan scheduler.
    Args:
        api_call (bool): Indicates whether the function was called via an API request.
    """
    global scheduler_task

    if not scheduler_task or scheduler_task.done():
        logger.warning("Scheduler is not running.")
        return {"status": "success", "message": "Scheduler is not running."}

    try:
        logger.info("Stopping the Azan scheduler...")
        scheduler_task.cancel()
        await scheduler_task  # Wait for the task to be canceled
        logger.info("Azan scheduler stopped successfully.")
        return {"status": "success", "message": "Azan scheduler stopped successfully."}
    except asyncio.CancelledError:
        logger.info("Scheduler task was canceled.")
        return {"status": "success", "message": "Azan scheduler stopped successfully."}
    except Exception as e:
        logger.error(f"❌ Failed to stop scheduler: {e}")
        return {"status": "error", "message": f"Failed to stop scheduler: {e}"}


async def restart_scheduler():
    """
    Restarts the Azan scheduler.
    """
    logger.info("Restarting the Azan scheduler...")
    try:
        # Stop the scheduler if it's running
        stop_result = await stop_scheduler()
        if stop_result["status"] == "success":
            # Start the scheduler
            start_result = await start_scheduler()
            if start_result["status"] == "success":
                logger.info("Azan scheduler restarted successfully.")
        return {"status": "success", "message": "Azan scheduler restarted successfully."}
    except Exception as e:
        logger.error(f"❌ Failed to restart scheduler: {e}")
        return {"status": "error", "message": f"Failed to restart scheduler: {e}"}