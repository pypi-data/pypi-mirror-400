"""Utility helper functions for common operations.

This module provides utility functions for data validation and timestamp generation
used across TinySDK services.

Example:
  Validating required keys::

    from tinysdk.utils import is_valid

    data = {"name": "John", "email": "john@example.com"}
    if is_valid(data, ["name", "email"]):
        print("Valid data")

  Getting UTC timestamp::

    from tinysdk.utils import get_date

    timestamp = get_date()  # Returns ISO 8601 string like "2024-01-08T12:30:45.123Z"
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


def is_valid(data: Dict[str, Any], keys: List[str]) -> bool:
  """
  Checks if all keys are in data

  Args:
      data (Dict[str, Any])
      keys (List[str])

  Returns:
      bool: true if all keys are in data otherwise false
  """
  if data is None or data == {}:
    return False
  return all(key in data for key in keys)


def get_date() -> str:
  """
  Get the current time in UTC and format it in ISO 8601 format

  Returns:
    Response: str: current date as a UTC ISO 8601 string with milliseconds
  """
  return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
