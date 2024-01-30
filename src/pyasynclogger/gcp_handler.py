"""Asynchronous handler for Google Cloud Logging"""
import asyncio
import logging

import google.cloud.logging
from google.cloud.logging_v2.handlers.transports.background_thread import _Worker


class AsyncGoogleCloudLoggingHandler(logging.Handler):
    """Asynchronous handler for Google Cloud Logging"""

    def __init__(self, gcp_client: google.cloud.logging.Client):
        super().__init__()
        self.client = gcp_client
        self.worker = _Worker(self.client, self.client.logger("python"), background_thread=False)  # type: ignore pylint: disable=too-many-function-args, unexpected-keyword-arg

    def emit(self, record):
        asyncio.create_task(self.async_emit(record))

    async def async_emit(self, record):
        """Asynchronously emit the record."""
        log_entry = self.format(record)
        # Use the Google Cloud Logging client to send the log entry
        await asyncio.get_event_loop().run_in_executor(None, self.worker.enqueue, log_entry)


# Instantiate a Google Cloud Logging client
client = google.cloud.logging.Client()

# Create and configure the asynchronous handler
async_handler = AsyncGoogleCloudLoggingHandler(client)
logging.getLogger().addHandler(async_handler)
