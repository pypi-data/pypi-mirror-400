"""Decorators for error handling and retry logic.

This module provides decorators used throughout TinySDK for logging exceptions
and implementing retry mechanisms with exponential backoff and jitter.

Example:
  Using exception_logger::

    from tinysdk.utils import exception_logger

    @exception_logger
    def risky_operation():
        # Automatically logs exceptions before re-raising
        return 1 / 0

  Using retry decorator::

    from tinysdk.utils import retry
    from pika.exceptions import AMQPConnectionError

    @retry(exceptions=(AMQPConnectionError,), tries=5, delay=5, backoff=2)
    def connect_to_rabbitmq():
        # Retries up to 5 times with exponential backoff
        pass
"""

import logging
import random
import time
from functools import wraps
from typing import Any, Callable, Tuple, Union


def exception_logger(func):
  """Decorator that logs exceptions before re-raising them.

  Wraps a function to automatically log any exceptions that occur during
  execution using the function's module logger. The exception is logged
  with the function name and error message, then re-raised.

  Args:
    func (Callable): The function to wrap

  Returns:
    Callable: Wrapped function with exception logging

  Example:
    >>> @exception_logger
    ... def my_function():
    ...     raise ValueError("Something went wrong")
    >>> my_function()  # Logs error and re-raises
  """

  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception as e:
      logger = logging.getLogger(func.__module__)
      logger.error(f"Error in {func.__name__}: {str(e)}")
      raise

  return wrapper


def retry(
  exceptions: Tuple[type, ...] = (Exception,),
  tries: int = 5,
  delay: int = 5,
  backoff: int = 1,
  jitter: Tuple[int, int] = (1, 3),
  logger: Union[logging.Logger, None] = None,
) -> Callable:
  """Decorator that retries a function with exponential backoff and jitter.

  Implements a retry mechanism with configurable exponential backoff and random
  jitter to prevent thundering herd problems. The function is retried on specified
  exception types up to a maximum number of attempts.

  Args:
    exceptions (Tuple[type, ...]): Tuple of exception types to catch and retry on.
      Defaults to (Exception,).
    tries (int): Maximum number of retry attempts. Defaults to 5.
    delay (int): Initial delay in seconds before first retry. Defaults to 5.
    backoff (int): Exponential backoff multiplier. Delay is multiplied by
      (backoff ** attempt) for each retry. Defaults to 1 (no backoff).
    jitter (Tuple[int, int]): Random jitter range (min, max) in seconds to add
      to each delay. Helps prevent synchronized retries. Defaults to (1, 3).
    logger (logging.Logger, optional): Logger instance for retry warnings and errors.

  Returns:
    Callable: Decorator function

  Raises:
    Exception: Raises "Maximum retries exceeded" if all retry attempts fail

  Example:
    >>> from pika.exceptions import AMQPConnectionError
    >>> @retry(exceptions=(AMQPConnectionError,), tries=5, delay=2, backoff=2)
    ... def connect():
    ...     # Will retry up to 5 times with 2s, 4s, 8s, 16s, 32s delays (+ jitter)
    ...     pass
  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
      attempt = 0
      while attempt < tries:
        try:
          return func(*args, **kwargs)
        except exceptions as e:
          attempt += 1
          if logger:
            logger.warning(f"Attempt {attempt} failed with exception: {str(e)}")
          sleep_time = delay * (backoff**attempt) + random.uniform(float(jitter[0]), float(jitter[1]))
          time.sleep(sleep_time)
      if logger:
        logger.error("Exceeded maximum number of connection retries.")
      raise Exception("Maximum retries exceeded")

    return wrapper

  return decorator
