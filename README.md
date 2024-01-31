# Asynchronous Logging with PyAsyncLogger

## Overview

PyAsyncLogger is an asynchronous logging library for Python, designed as a drop-in replacement for the standard logging library. It enhances logging in asynchronous environments by ensuring that logging operations don't block the main execution flow. Key features include:

- **Asynchronous logging:** Logs messages asynchronously to avoid performance bottlenecks.
- **Context binding:** Enhances log messages with additional context for more comprehensive analysis.
- **Customizable handlers:** Supports various output formats and destinations, including popular cloud services.
- **Easy integration:** Designed for seamless integration into existing Python projects with minimal code changes.

## Installation

Install using pip:

```bash
pip install pyasynclogger
```

## Basic Usage

To use PyAsyncLogger, simply replace the standard logging import with PyAsyncLogger. The library automatically configures the appropriate logging handler based on the `ASYNC_LOGGING_HANDLER` environment variable.

```python
import pyasynclogger as logging

logger = logging.getLogger("my_logger")
logger.info("This is an informational message")
logger.warning("This is a warning message")
```

By default, PyAsyncLogger uses a stream handler (stdout/stderr). To use a specific cloud provider's logging service, set the `ASYNC_LOGGING_HANDLER` environment variable to one of the following values: `gcp`, `aws`, `azure`. Configure the necessary credentials and settings as required by the respective cloud provider.

### Example: Using Google Cloud Logging

1. Set the environment variable:

   ```bash
   export ASYNC_LOGGING_HANDLER=gcp
   ```

2. Ensure you have the necessary credentials configured for Google Cloud.

3. Use the logger as usual in your code.

### Example: Using AWS CloudWatch

1. Set the environment variable:

   ```bash
   export ASYNC_LOGGING_HANDLER=aws
   ```

2. Configure your AWS credentials and settings.

3. Use the logger in your application.

### Example: Using Azure Monitor Logging

1. Set the environment variable:

   ```bash
   export ASYNC_LOGGING_HANDLER=azure
   ```

    Also Microsoft, being Microsoft requires you to set two more environment variables.
    Don't blame me, talk to Staya

    ```bash
        export LOGS_DCR_RULE_ID = <Your Azure Rule ID>
        export LOGS_DCR_STREAM_NAME = <Your Azure Stream Name>
    ```

2. Configure Azure credentials and settings.

3. Implement logging in your code.

## Contributing

We welcome contributions! Please refer to the contribution guidelines in the GitHub repository.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please reach out to [Jacob Bourne](mailto:jacob.bourne@gmail.com).
