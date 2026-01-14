"""Tests for TinyStorageHandler."""

import pytest

from tinysdk import TinyStorageHandler


def test_tinystoragehandler_import():
  """Test that TinyStorageHandler can be imported."""
  assert TinyStorageHandler is not None


def test_tinystoragehandler_initialization_with_params(minio_credentials):
  """Test TinyStorageHandler initialization with explicit parameters."""
  storage = TinyStorageHandler(**minio_credentials)
  assert storage.endpoint == minio_credentials["endpoint"]
  assert storage.access_key == minio_credentials["access_key"]
  assert storage.secret_key == minio_credentials["secret_key"]


def test_tinystoragehandler_initialization_without_params_fails():
  """Test that TinyStorageHandler initialization fails without credentials."""
  with pytest.raises(AssertionError):
    TinyStorageHandler()


def test_tinystoragehandler_has_expected_methods():
  """Test that TinyStorageHandler has expected methods."""
  assert hasattr(TinyStorageHandler, "upload_file")
  assert hasattr(TinyStorageHandler, "download_file")
  assert hasattr(TinyStorageHandler, "upload_folder")
  assert hasattr(TinyStorageHandler, "download_folder")
  assert hasattr(TinyStorageHandler, "delete_file")
  assert hasattr(TinyStorageHandler, "delete_folder")
  assert hasattr(TinyStorageHandler, "list_objects")
  assert hasattr(TinyStorageHandler, "object_exists")
  assert hasattr(TinyStorageHandler, "close")
