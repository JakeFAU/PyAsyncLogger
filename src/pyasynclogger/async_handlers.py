"""Asynchronous logging handlers for Google Cloud Logging, Azure Monitor, and AWS CloudWatch Logs."""
import asyncio
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import TextIO

import boto3
import google.cloud.logging
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from google.cloud.logging_v2.handlers.transports.background_thread import _Worker


class AsyncLoggingHandler(logging.Handler, ABC):
    """
    An abstract base class for asynchronous logging handlers.

    This class defines the basic structure for asynchronous logging handlers
    and enforces the implementation of the async_emit method in derived classes.
    """

    def emit(self, record: logging.LogRecord):
        """
        Emit a logging record.

        Overrides the emit method of logging.Handler to schedule the async_emit
        method as an asyncio task, enabling asynchronous logging.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        asyncio.create_task(self.async_emit(record))

    @abstractmethod
    async def async_emit(self, record: logging.LogRecord):
        """
        Asynchronously emit a logging record.

        This method should be implemented by subclasses to define asynchronous
        logging behavior.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """


class AsyncGoogleCloudLoggingHandler(AsyncLoggingHandler):
    """
    Asynchronous logging handler for Google Cloud Logging.

    This handler asynchronously sends logging records to Google Cloud Logging.

    Attributes:
        client (google.cloud.logging.Client): The Google Cloud Logging client.
        worker (_Worker): The worker instance used to enqueue log messages.
    """

    def __init__(self, gcp_client: google.cloud.logging.Client):
        """
        Initialize the AsyncGoogleCloudLoggingHandler.

        Args:
            gcp_client (google.cloud.logging.Client): The Google Cloud Logging client.
        """
        super().__init__()
        self.client = gcp_client
        self.worker = _Worker(
            cloud_logger=self.client.logger("python"),
            grace_period=0.5,
            max_batch_size=32,
            max_latency=5,
        )

    async def async_emit(self, record: logging.LogRecord):
        """
        Asynchronously emit the logging record to Google Cloud Logging.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        log_entry = self.format(record)
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.worker.enqueue(record, log_entry)
        )


class AsyncAzureMonitorLoggingHandler(AsyncLoggingHandler):
    """
    Asynchronous logging handler for Azure Monitor Logging.

    This handler asynchronously sends logging records to Azure Monitor.

    Attributes:
        client (LogsIngestionClient): The Azure Monitor LogsIngestion client.
        rule_id (str): The rule ID for data collection.
        stream_name (str): The stream name for data collection.
    """

    def __init__(self):
        """
        Initialize the AsyncAzureMonitorLoggingHandler.
        """
        super().__init__()
        endpoint = os.environ["DATA_COLLECTION_ENDPOINT"]
        credential = DefaultAzureCredential()
        self.client = LogsIngestionClient(
            endpoint=endpoint, credential=credential, logging_enable=True
        )
        self.rule_id = os.environ["LOGS_DCR_RULE_ID"]
        self.stream_name = os.environ["LOGS_DCR_STREAM_NAME"]

    async def async_emit(self, record: logging.LogRecord):
        """
        Asynchronously emit the logging record to Azure Monitor.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        log_entry = self.format(record)
        body = [{"Time": record.asctime, "Level": record.levelname, "Message": log_entry}]

        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.upload, self.rule_id, self.stream_name, body
            )
        except HttpResponseError as e:
            print(f"Upload failed: {e}")


class AsyncCloudWatchLoggingHandler(AsyncLoggingHandler):
    """
    Asynchronous logging handler for AWS CloudWatch Logging.

    This handler asynchronously sends logging records to AWS CloudWatch.

    Attributes:
        client: The boto3 CloudWatch Logs client.
        log_group_name (str): The name of the CloudWatch Logs log group.
        stream_name (str): The name of the CloudWatch Logs stream.
        sequence_token (str): The sequence token for the log stream.
    """

    def __init__(self, log_group_name: str, stream_name: str):
        """
        Initialize the AsyncCloudWatchLoggingHandler.

        Args:
            log_group_name (str): The name of the CloudWatch Logs log group.
            stream_name (str): The name of the CloudWatch Logs stream.
        """
        super().__init__()
        self.client = boto3.client("logs")
        self.log_group_name = log_group_name
        self.stream_name = stream_name
        self.sequence_token = None

    async def async_emit(self, record: logging.LogRecord):
        """
        Asynchronously emit the logging record to AWS CloudWatch Logs.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        log_entry = self.format(record)
        log_event = {"timestamp": int(record.created * 1000), "message": log_entry}

        def put_log_events():
            return self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.stream_name,
                logEvents=[log_event],
                sequenceToken=self.sequence_token if self.sequence_token else None,
            )

        response = await asyncio.get_event_loop().run_in_executor(None, put_log_events)
        self.sequence_token = response.get("nextSequenceToken")


class StreamLoggingHandler(AsyncLoggingHandler):
    """A handler that writes to stdout or stderr."""

    terminator: str

    def __init__(self, stream: TextIO = sys.stdout, terminator="\n"):
        super().__init__()
        if stream is None:
            stream = sys.stderr
        self.stream = stream
        self.terminator = terminator

    async def async_emit(self, record: logging.LogRecord):
        msg = self.format(record)
        stream = self.stream
        stream.write(msg)
        stream.write(self.terminator)
        stream.flush()
