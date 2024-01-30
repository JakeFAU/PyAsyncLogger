# Asynchronous Logging with PyAsyncLogger

## Overview

This library provides asynchronous logging capabilities for Python applications, ensuring that logging operations don't block the main execution flow, making it ideal for asynchronous environments. It's designed as a drop-in replacement for the standard logging library, with a few key enhancements:

- **Asynchronous logging:** Logs messages asynchronously, preventing performance bottlenecks.
- **Context binding:** Allows associating additional context with log messages, providing more comprehensive data for analysis.
- **Customizable handlers:** Supports different output formats and destinations for logs, suiting various needs.
- **Easy to use:** Designed for seamless integration into existing Python projects.

## Installation

Install using pip:

```bash
pip install pyasynclogger
```

## Basic Usage

1. **Import the AsyncLogger class:**

```python
import pyasynclogger as logging
```

2. **Create an AsyncLogger instance:**

```python
logger = logging.get_logger("my_logger")
```

3. **Use logging methods:**

```python
logger.info("This is an informational message")
logger.warning("This is a warning message")
```

4. **Use context binding:**

```python
logger.bind(user_id=123, session_id="abc123")
logger.info("User 123 started a new session")
```

## Additional Features

- **Custom handlers:**

```python
# TODO: Add examples of custom handlers
```

## Contributing

We welcome contributions! Please refer to the contribution guidelines in the GitHub repository.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please reach out to [Jacob Bourne]([jacob.bourne@gmail.com]).
