"""This is used to set a handler to the root logger in the init"""
import os
import logging
from .async_handlers import (
    AsyncGoogleCloudLoggingHandler,
    AsyncAzureMonitorLoggingHandler,
    AsyncCloudWatchLoggingHandler,
    StreamLoggingHandler,
)


def get_logging_handler():
    """Get the logging handler based on the environment variable ASYNC_LOGGING_HANDLER."""
    handlers = {
        "gcp": AsyncGoogleCloudLoggingHandler,
        "aws": AsyncCloudWatchLoggingHandler,
        "azure": AsyncAzureMonitorLoggingHandler,
        "stream": StreamLoggingHandler,  # Default handler
    }
    handler_type = os.getenv("ASYNC_LOGGING_HANDLER", "stream").lower()
    return handlers.get(handler_type, StreamLoggingHandler)()


def setup_logging():
    """Set up the logging handler for the root logger."""
    handler = get_logging_handler()
    logging.getLogger().addHandler(handler)


setup_logging()
