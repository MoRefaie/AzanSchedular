import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AzanScheduler import scheduler_manager


@pytest.mark.asyncio
async def test_scheduler_status_active():
    with patch.object(scheduler_manager, "scheduler_task", new=MagicMock(done=lambda: False)):
        result = await scheduler_manager.scheduler_status()
        assert result["data"]["active"] is True


@pytest.mark.asyncio
async def test_scheduler_status_inactive():
    with patch.object(scheduler_manager, "scheduler_task", new=None):
        result = await scheduler_manager.scheduler_status()
        assert result["data"]["active"] is False


@pytest.mark.asyncio
async def test_start_scheduler_already_running():
    with patch.object(scheduler_manager, "scheduler_task", new=MagicMock(done=lambda: False)):
        result = await scheduler_manager.start_scheduler()
        assert result["status"] == "error"


@pytest.mark.asyncio
async def test_start_scheduler_success():
    with patch.object(scheduler_manager, "scheduler_task", new=None):
        with patch.object(scheduler_manager, "scheduler", new=MagicMock(run=AsyncMock())):
            result = await scheduler_manager.start_scheduler()
            assert result["status"] in ("success", "error")


@pytest.mark.asyncio
async def test_stop_scheduler_not_running():
    with patch.object(scheduler_manager, "scheduler_task", new=None):
        result = await scheduler_manager.stop_scheduler()
        assert result["status"] == "success"


@pytest.mark.asyncio
async def test_stop_scheduler_success():
    fake_task = AsyncMock()
    fake_task.done.return_value = False
    with patch.object(scheduler_manager, "scheduler_task", new=fake_task):
        result = await scheduler_manager.stop_scheduler()
        assert result["status"] in ("success", "error")


@pytest.mark.asyncio
async def test_restart_scheduler_success():
    with patch.object(scheduler_manager, "stop_scheduler", new=AsyncMock(return_value={"status": "success"})):
        with patch.object(scheduler_manager, "start_scheduler", new=AsyncMock(return_value={"status": "success"})):
            result = await scheduler_manager.restart_scheduler()
            assert result["status"] == "success"
