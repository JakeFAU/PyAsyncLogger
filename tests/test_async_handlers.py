import logging
from unittest.mock import ANY, MagicMock, patch

import boto3

import pytest

from pyasynclogger.async_handlers import (
    AsyncGoogleCloudLoggingHandler,
    AsyncAzureMonitorLoggingHandler,
    AsyncCloudWatchLoggingHandler,
)

# first we need to create mock versions of GCP, Azure and AWS clients
# we will use the MagicMock class to achieve this

# Create a mock instance of the Google Cloud Logging client
google_cloud_logging_client = MagicMock()

# Create a mock instance of the AWS CloudWatch client
boto3.client = MagicMock()

# Create a mock instance of the Azure Monitor client
azure_monitor_client = MagicMock()


@pytest.fixture
def mock_boto3_client():
    with patch("boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_env_vars(monkeypatch):
    # Set mock environment variables
    monkeypatch.setenv("DATA_COLLECTION_ENDPOINT", "https://example.com")
    monkeypatch.setenv("LOGS_DCR_RULE_ID", "test_rule_id")
    monkeypatch.setenv("LOGS_DCR_STREAM_NAME", "test_stream_name")
    yield


@pytest.mark.asyncio
async def test_async_google_cloud_logging_handler():
    """Test the AsyncGoogleCloudLoggingHandler class"""
    # Create an instance of the AsyncGoogleCloudLoggingHandler class
    handler = AsyncGoogleCloudLoggingHandler(
        gcp_client=google_cloud_logging_client,
    )

    # Create a mock log record
    record = logging.LogRecord(
        name="TestLogger",
        level=logging.INFO,
        pathname="test_async_handlers.py",
        lineno=42,
        msg="This is a test log message",
        args=(),
        exc_info=None,
    )

    with patch("pyasynclogger.async_handlers._Worker.enqueue") as mock_enqueue:
        # Call the async_emit method on the handler
        await handler.async_emit(record)

        # Verify that enqueue was called correctly
        mock_enqueue.assert_called_once_with(record, ANY)

    # Verify that the handler's client and worker attributes were set correctly
    assert handler.client == google_cloud_logging_client
    assert handler.worker._cloud_logger == google_cloud_logging_client.logger("python")  # pylint: disable=protected-access
    assert handler.worker._grace_period == 0.5  # pylint: disable=protected-access
    assert handler.worker._max_batch_size == 32  # pylint: disable=protected-access
    assert handler.worker._max_latency == 5  # pylint: disable=protected-access


# Mock Azure credential
class MockDefaultAzureCredential:
    pass


@pytest.mark.asyncio
async def test_async_azure_monitor_logging_handler(mock_env_vars):
    """Test the AsyncAzureMonitorLoggingHandler class"""
    with patch("pyasynclogger.async_handlers.DefaultAzureCredential", MockDefaultAzureCredential):
        # Create an instance of the AsyncAzureMonitorLoggingHandler class
        handler = AsyncAzureMonitorLoggingHandler()

    # Create a mock log record
    record = logging.LogRecord(
        name="TestLogger",
        level=logging.INFO,
        pathname="test_async_handlers.py",
        lineno=42,
        msg="This is a test log message",
        args=(),
        exc_info=None,
    )
    record.asctime = "2024-01-30 10:00:00"

    # Mock the client's upload method
    with patch.object(handler.client, "upload", autospec=True) as mock_upload:
        # Call the async_emit method on the handler
        await handler.async_emit(record)

        # Verify that upload was called correctly
        mock_upload.assert_called_once_with(
            "test_rule_id",
            "test_stream_name",
            [
                {
                    "Time": "2024-01-30 10:00:00",
                    "Level": "INFO",
                    "Message": "This is a test log message",
                }
            ],
        )

    # Additional assertions for handler attributes
    assert handler.rule_id == "test_rule_id"
    assert handler.stream_name == "test_stream_name"


@pytest.mark.asyncio
async def test_async_cloudwatch_logging_handler(mock_boto3_client):
    """Test the AsyncCloudWatchLoggingHandler class"""
    log_group_name = "test_log_group"
    stream_name = "test_stream"

    # Create an instance of the AsyncCloudWatchLoggingHandler class
    handler = AsyncCloudWatchLoggingHandler(
        log_group_name=log_group_name,
        stream_name=stream_name,
    )

    # Create a mock log record
    record = logging.LogRecord(
        name="TestLogger",
        level=logging.INFO,
        pathname="test_async_handlers.py",
        lineno=42,
        msg="This is a test log message",
        args=(),
        exc_info=None,
    )
    record.created = 1651012500.0  # Example timestamp

    # Mock the client's put_log_events method
    with patch.object(handler.client, "put_log_events") as mock_put_log_events:
        # Call the async_emit method on the handler
        await handler.async_emit(record)

        # Verify that put_log_events was called correctly
        expected_log_event = {
            "timestamp": int(record.created * 1000),
            "message": "This is a test log message",
        }
        mock_put_log_events.assert_called_once_with(
            logGroupName=log_group_name,
            logStreamName=stream_name,
            logEvents=[expected_log_event],
            sequenceToken=None,
        )

    # Additional assertions for handler attributes
    assert handler.log_group_name == log_group_name
    assert handler.stream_name == stream_name
