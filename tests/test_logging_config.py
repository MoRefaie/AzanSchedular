import pytest
from unittest.mock import patch, MagicMock
from AzanSchedular.logging_config import get_console_logging_setting, get_logger, configure_logger
import logging

def test_dummy():
    assert True

def test_get_console_logging_setting_returns_bool():
    with patch("builtins.open", patch("builtins.open", create=True)):
        assert isinstance(get_console_logging_setting(), bool)

def test_get_logger_returns_logger():
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)

def test_configure_logger_adds_handlers(monkeypatch):
    root_logger = logging.getLogger()
    # Remove all handlers first
    root_logger.handlers = []
    monkeypatch.setattr("AzanSchedular.logging_config.console_logging", False)
    configure_logger()
    assert any(isinstance(h, logging.Handler) for h in root_logger.handlers)
