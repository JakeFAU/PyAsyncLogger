"""Async Logging Module

This module provides an asynchronous logging system, allowing logs to be handled
without blocking the main execution flow in asynchronous applications.

Classes:
    AsyncLogHandler: A handler for asynchronous logging.
    AsyncLogger: A logger class that supports asynchronous logging operations.

Functions:
    main: An example usage of the AsyncLogger and AsyncLogHandler.
"""
import asyncio
import json
import logging
import sys
from collections import deque
from logging import Logger, LogRecord
from types import TracebackType
from typing import Mapping, TypeAlias

from src.pyasynclogger.json_tools import CustomJSONEncoder

_ArgsType: TypeAlias = tuple[object, ...] | Mapping[str, object]
_SysExcInfoType: TypeAlias = (
    tuple[type[BaseException], BaseException, TracebackType | None] or tuple[None, None, None]
)


class AsyncLogHandler(logging.Handler):
    """A handler class for asynchronous logging.

    This handler stores log records in a deque and uses an asynchronous loop to
    process them, allowing for non-blocking logging operations.

    Attributes:
        buffer (deque): A deque used to store log records.
        loop (asyncio.AbstractEventLoop): The event loop used for asynchronous operations.

    Methods:
        emit(record): Stores a log record in the buffer.
        flush_logs(): Asynchronously flushes logs from the buffer.
    """

    def __init__(self):
        super().__init__()
        self.buffer = deque()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.flush_logs())

    def emit(self, record):
        """Stores a log record in the buffer.

        Args:
            record (LogRecord): The log record to be stored.
        """
        self.buffer.append(self.format(record))

    async def flush_logs(self):
        """Asynchronously flushes logs from the buffer.

        This method continuously processes and outputs log records from the buffer.
        """
        while True:
            while self.buffer:
                record = self.buffer.popleft()
                # Implement your asynchronous I/O operation here
                print(record)  # Placeholder for actual I/O operation
            await asyncio.sleep(1)  # Adjust the sleep duration as needed


class AsyncLogger(Logger):
    """A logger class that supports asynchronous logging operations.

    This logger extends the standard Logger class, adding support for asynchronous
    log handling. It allows binding additional context to each log message.

    Attributes:
        context (dict): A dictionary of context information for log messages.

    Methods:
        bind(**new_context): Binds new context information to the logger.
        makeRecord(...): Creates a log record with the additional context.
        _log_async(level, msg, *args, **kwargs): Asynchronously logs a message.
        handle(record): Asynchronously handles a log record.
        debug, info, warning, error, critical: Asynchronous logging methods..
        get_logger(name, level, context): Class method to get or create an AsyncLogger instance.
    """

    _loggers = {}

    def __init__(self, name, level=logging.NOTSET, context=None):
        """Initializes the AsyncLogger.

        Args:
            name (str): The name of the logger.
            level (int): The logging level.
            context (dict, optional): Additional context for log messages.
        """
        super().__init__(name, level)
        self.context = context or {}

    def bind(self, **new_context):
        """Binds new context information to the logger.

        Args:
            **new_context: Arbitrary keyword arguments representing new context information.
        """
        self.context.update(new_context)

    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args: _ArgsType,
        exc_info: _SysExcInfoType | None,
        func: str | None = None,
        extra: Mapping[str, object] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        """Creates a log record with additional context.

        This method extends the standard logging.Logger's makeRecord method by
        adding the logger's context to the log record.

        Args:
            name (str): The name of the logger.
            level (int): The numeric level of the logging event (e.g., logging.DEBUG).
            fn (str): The filename where the logging call was made.
            lno (int): The line number where the logging call was made.
            msg (object): The event description message, possibly a format string.
            args (_ArgsType): The arguments to merge into msg if it's a format string.
            exc_info (_SysExcInfoType | None): Exception tuple (type, value, traceback) or None.
            func (str | None): The function name where the logging call was made.
            extra (Mapping[str, object] | None): Additional context added to the log record.
                                                 This must be JSON serializable using the
                                                 fryday_lib.utils.strings.CustomJSONEncoder.
            sinfo (str | None): Stack information from the bottom of the call stack.

        Returns:
            LogRecord: A LogRecord instance representing the logging event.

        Raises:
            ValueError: If values in 'extra' are not JSON serializable.
        """
        if extra is None:
            extra = {}
        else:
            try:
                json.dumps(extra, cls=CustomJSONEncoder)  # Test if 'extra' is JSON serializable
            except (TypeError, ValueError) as e:
                raise ValueError("Non-serializable data provided in 'extra'") from e

        extra.update(self.context)  # type: ignore
        return super().makeRecord(
            name=name,
            level=level,
            fn=fn,
            lno=lno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=func,
            extra=extra,
            sinfo=sinfo,
        )

    async def _log_async(self, level, msg, *args, **kwargs):
        """Asynchronously logs a message at a specified level.

        This internal method creates a log record and passes it to the handler
        if the logger is enabled for the specified severity level.

        Args:
            level (int): The numeric level of the logging event (e.g., logging.INFO).
            msg (str): The event description message, possibly a format string.
            *args: Arguments to merge into msg if it's a format string.
            **kwargs: Arbitrary keyword arguments. Commonly used keywords include:
                - fn (str): Filename where the logging call was made.
                - lno (int): Line number where the logging call was made.
                - exc_info (_SysExcInfoType | None): Exception info tuple or None.
                - extra (Mapping[str, object] | None): Additional context for the log record.
                - sinfo (str | None): Stack information from the call.

        Note:
            This method should not be called directly; use the specific logging
            methods like debug(), info(), etc.
        """
        if self.isEnabledFor(level):
            record = self.makeRecord(
                name=self.name,
                level=level,
                fn=kwargs.get("fn", ""),
                lno=kwargs.get("lno", None),
                msg=msg,
                args=args,
                exc_info=kwargs.get("exc_info"),
                extra=kwargs.get("extra"),
                sinfo=kwargs.get("sinfo"),
            )
            await self.handle(record)

    async def handle(self, record):  #  pylint: disable=invalid-overridden-method
        """Asynchronously handles a log record.

        This method asynchronously dispatches the log record to all the handlers
        associated with this logger.

        Args:
            record (LogRecord): The log record to be handled.

        Note:
            This method overrides the standard logging.Logger's handle method
            to introduce asynchronous handling.
        """
        for handler in self.handlers:
            await asyncio.create_task(handler.handle(record))  # type: ignore

    # Async versions of standard logging methods
    async def debug(self, msg, *args, **kwargs):  #  pylint: disable=invalid-overridden-method
        """Asynchronously logs a debug message.

        This method logs a message with a severity level of 'DEBUG'. It is an
        asynchronous version of the standard logging library's debug method, ensuring
        that logging does not block the main execution flow in asynchronous applications.

        Args:
            msg (str): The message to be logged. This can be a format string, which will
                    be merged with `args` using the string formatting operator.
            *args: Variable length argument list. These arguments are merged into `msg`
                using the string formatting operator, allowing dynamic message formatting.
            **kwargs: Arbitrary keyword arguments. These can include additional context or
                    parameters specific to the logging handler's implementation. For
                    example, `exc_info` to include exception information, `stack_info`
                    to include stack information, or any custom additional information
                    that should be included in the log record.

        Example:
            await logger.debug("This is a debug message with value: %s", value)

        Note:
            The actual output format and destination of the log message depend on the
            configuration of the logger's handlers.
        """
        try:
            await self._log_async(logging.DEBUG, msg, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # I am using print here because the logger itself is not working
            print("DEBUG: An error occurred while logging:\n%s", e, file=sys.stderr)
            print("DEBUG: Message that failed to log:\n%s", msg, file=sys.stderr)

    async def info(self, msg, *args, **kwargs):  #  pylint: disable=invalid-overridden-method
        """Asynchronously logs a info message.

        This method logs a message with a severity level of 'INFO'. It is an
        asynchronous version of the standard logging library's info method, ensuring
        that logging does not block the main execution flow in asynchronous applications.

        Args:
            msg (str): The message to be logged. This can be a format string, which will
                    be merged with `args` using the string formatting operator.
            *args: Variable length argument list. These arguments are merged into `msg`
                using the string formatting operator, allowing dynamic message formatting.
            **kwargs: Arbitrary keyword arguments. These can include additional context or
                    parameters specific to the logging handler's implementation. For
                    example, `exc_info` to include exception information, `stack_info`
                    to include stack information, or any custom additional information
                    that should be included in the log record.

        Example:
            await logger.info("This is a info message with value: %s", value)

        Note:
            The actual output format and destination of the log message depend on the
            configuration of the logger's handlers.
        """
        try:
            await self._log_async(logging.INFO, msg, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # I am using print here because the logger itself is not working
            print("INFO: An error occurred while logging:\n%s", e, file=sys.stderr)
            print("INFO: Message that failed to log:\n%s", msg, file=sys.stderr)

    async def warning(self, msg, *args, **kwargs):  #  pylint: disable=invalid-overridden-method
        """Asynchronously logs a warning message.

        This method logs a message with a severity level of 'WARNING'. It is an
        asynchronous version of the standard logging library's warning method, ensuring
        that logging does not block the main execution flow in asynchronous applications.

        Args:
            msg (str): The message to be logged. This can be a format string, which will
                    be merged with `args` using the string formatting operator.
            *args: Variable length argument list. These arguments are merged into `msg`
                using the string formatting operator, allowing dynamic message formatting.
            **kwargs: Arbitrary keyword arguments. These can include additional context or
                    parameters specific to the logging handler's implementation. For
                    example, `exc_info` to include exception information, `stack_info`
                    to include stack information, or any custom additional information
                    that should be included in the log record.

        Example:
            await logger.warning("This is a warning message with value: %s", value)

        Note:
            The actual output format and destination of the log message depend on the
            configuration of the logger's handlers.
        """
        try:
            await self._log_async(logging.WARNING, msg, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # I am using print here because the logger itself is not working
            print("WARNING: An error occurred while logging:\n%s", e, file=sys.stderr)
            print("WARNING: Message that failed to log:\n%s", msg, file=sys.stderr)

    async def error(self, msg, *args, **kwargs):  #  pylint: disable=invalid-overridden-method
        """Asynchronously logs a error message.

        This method logs a message with a severity level of 'ERROR'. It is an
        asynchronous version of the standard logging library's error method, ensuring
        that logging does not block the main execution flow in asynchronous applications.

        Args:
            msg (str): The message to be logged. This can be a format string, which will
                    be merged with `args` using the string formatting operator.
            *args: Variable length argument list. These arguments are merged into `msg`
                using the string formatting operator, allowing dynamic message formatting.
            **kwargs: Arbitrary keyword arguments. These can include additional context or
                    parameters specific to the logging handler's implementation. For
                    example, `exc_info` to include exception information, `stack_info`
                    to include stack information, or any custom additional information
                    that should be included in the log record.

        Example:
            await logger.error("This is an error message with value: %s", value)

        Note:
            The actual output format and destination of the log message depend on the
            configuration of the logger's handlers.
        """
        try:
            await self._log_async(logging.ERROR, msg, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # I am using print here because the logger itself is not working
            print("ERROR: An error occurred while logging:\n%s", e, file=sys.stderr)
            print("ERROR: Message that failed to log:\n%s", msg, file=sys.stderr)

    async def critical(self, msg, *args, **kwargs):  #  pylint: disable=invalid-overridden-method
        """Asynchronously logs a critical message.

        This method logs a message with a severity level of 'CRITICAL'. It is an
        asynchronous version of the standard logging library's critical method, ensuring
        that logging does not block the main execution flow in asynchronous applications.

        Args:
            msg (str): The message to be logged. This can be a format string, which will
                    be merged with `args` using the string formatting operator.
            *args: Variable length argument list. These arguments are merged into `msg`
                using the string formatting operator, allowing dynamic message formatting.
            **kwargs: Arbitrary keyword arguments. These can include additional context or
                    parameters specific to the logging handler's implementation. For
                    example, `exc_info` to include exception information, `stack_info`
                    to include stack information, or any custom additional information
                    that should be included in the log record.

        Example:
            await logger.critical("This is a critical message with value: %s", value)

        Note:
            The actual output format and destination of the log message depend on the
            configuration of the logger's handlers.
        """
        try:
            await self._log_async(logging.CRITICAL, msg, *args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # I am using print here because the logger itself is not working
            print("CRITICAL: An error occurred while logging:\n%s", e, file=sys.stderr)
            print("CRITICAL: Message that failed to log:\n%s", msg, file=sys.stderr)

    @classmethod
    def get_logger(cls, name, level=logging.NOTSET, context=None):  #  pylint: disable=invalid-name
        """Gets or creates an AsyncLogger instance.

        Args:
            name (str): The name of the logger.
            level (int): The logging level.
            context (dict, optional): Additional context for log messages.

        Returns:
            AsyncLogger: An instance of AsyncLogger.
        """
        if name not in cls._loggers:
            cls._loggers[name] = cls(name, level, context)
        return cls._loggers[name]


def getLogger(name, level=logging.NOTSET, context=None):  #  pylint: disable=invalid-name
    """Gets or creates an AsyncLogger instance."""
    return AsyncLogger.get_logger(name, level, context)
