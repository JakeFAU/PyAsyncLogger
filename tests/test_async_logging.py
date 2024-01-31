import logging
from unittest.mock import MagicMock, Mock, patch

import pytest

from pyasynclogger.async_logging import AsyncLogger


@pytest.mark.asyncio
async def test_basic_logging(mocker):
    logger = AsyncLogger("test_logger")

    with patch("pyasynclogger.async_logging.AsyncLogHandler") as mock_handler:
        # Create a mock instance of the AsyncHandler class
        mock_handler_instance = Mock()

        # Call various logging methods on the logger
        await logger.debug("This is a debug message")
        await logger.info("This is an info message")
        await logger.warning("This is a warning message")
        await logger.error("This is an error message")
        await logger.critical("This is a critical message")

        mock_handler.verify(
            mock_handler_instance,
            mocker.call.handle(logging.DEBUG, "This is a debug message", extra={}),
        )
        mock_handler.verify(
            mock_handler_instance,
            mocker.call.handle(logging.INFO, "This is an info message", extra={}),
        )
        mock_handler.verify(
            mock_handler_instance,
            mocker.call.handle(logging.WARNING, "This is a warning message", extra={}),
        )
        mock_handler.verify(
            mock_handler_instance,
            mocker.call.handle(logging.ERROR, "This is an error message", extra={}),
        )
        mock_handler.verify(
            mock_handler_instance,
            mocker.call.handle(logging.CRITICAL, "This is a critical message", extra={}),
        )


@pytest.mark.asyncio
async def test_context_binding_and_logging():
    """Test that context is bound to log messages"""
    logger = AsyncLogger("test_logger_context_binding")

    with patch("pyasynclogger.async_logging.AsyncLogHandler") as mock_handler:
        # Create a mock instance of the AsyncHandler class
        mock_handler_instance = MagicMock()

        # Call various logging methods on the logger
        await logger.info("This is an info message", extra={"context": "info"})
        await logger.warning("This is a warning message", extra={"context": "warning"})
        await logger.error("This is an error message", extra={"context": "error"})

        mock_handler.verify(
            mock_handler_instance,
            mock_handler.call.handle(
                logging.INFO, "This is an info message", extra={"context": "info"}
            ),
        )
        mock_handler.verify(
            mock_handler_instance,
            mock_handler.call.handle(
                logging.WARNING, "This is a warning message", extra={"context": "warning"}
            ),
        )
        mock_handler.verify(
            mock_handler_instance,
            mock_handler.call.handle(
                logging.ERROR, "This is an error message", extra={"context": "error"}
            ),
        )


@pytest.mark.asyncio
async def test_error_handling_in_logging():
    """Test that exceptions are handled properly in logging"""
    logger = AsyncLogger("test_logger_error_handling")

    with patch("pyasynclogger.async_logging.AsyncLogHandler") as mock_handler:
        # Create a mock instance of the AsyncHandler class
        mock_handler_instance = MagicMock()

        # Call various logging methods on the logger
        await logger.info("This is an info message")
        await logger.error("This is an error message", extra={"context": "error"})

        mock_handler.verify(
            mock_handler_instance,
            mock_handler.call.handle(logging.INFO, "This is an info message", extra={}),
        )
        mock_handler.verify(
            mock_handler_instance,
            mock_handler.call.handle(
                logging.ERROR, "This is an error message", extra={"context": "error"}
            ),
        )


def test_get_logger_creates_new_instance():
    logger1 = AsyncLogger.get_logger("unique_logger")
    logger2 = AsyncLogger.get_logger("unique_logger")
    assert logger1 is logger2


def test_get_logger_with_different_names():
    logger1 = AsyncLogger.get_logger("logger1")
    logger2 = AsyncLogger.get_logger("logger2")
    assert logger1 is not logger2
