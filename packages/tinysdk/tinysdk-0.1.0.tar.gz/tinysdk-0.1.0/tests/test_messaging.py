"""Tests for TinyMessageService and TinyMessageServiceSync."""

import pytest

from tinysdk import TinyMessageService, TinyMessageServiceSync


def test_tinymessageservice_import():
  """Test that TinyMessageService can be imported."""
  assert TinyMessageService is not None
  assert TinyMessageServiceSync is not None


def test_tinymessageservice_initialization_with_params(rabbitmq_credentials):
  """Test TinyMessageService initialization with explicit parameters."""
  queue_settings = [("test-queue", lambda msg: None)]
  msg_service = TinyMessageService(queue_settings=queue_settings, **rabbitmq_credentials)
  assert msg_service.host == rabbitmq_credentials["host"]
  assert msg_service.port == rabbitmq_credentials["port"]
  assert msg_service.user == rabbitmq_credentials["user"]
  assert msg_service.password == rabbitmq_credentials["password"]


def test_tinymessageservicesync_initialization_with_params(rabbitmq_credentials):
  """Test TinyMessageServiceSync initialization with explicit parameters."""
  msg_service = TinyMessageServiceSync(**rabbitmq_credentials)
  assert msg_service.host == rabbitmq_credentials["host"]
  assert msg_service.port == rabbitmq_credentials["port"]
  assert msg_service.user == rabbitmq_credentials["user"]
  assert msg_service.password == rabbitmq_credentials["password"]


def test_tinymessageservice_initialization_without_params_fails():
  """Test that TinyMessageService initialization fails without credentials."""
  queue_settings = [("test-queue", lambda msg: None)]
  with pytest.raises(AssertionError):
    TinyMessageService(queue_settings=queue_settings)


def test_tinymessageservicesync_initialization_without_params_fails():
  """Test that TinyMessageServiceSync initialization fails without credentials."""
  with pytest.raises(AssertionError):
    TinyMessageServiceSync()


def test_tinymessageservice_has_expected_methods():
  """Test that TinyMessageService has expected methods."""
  assert hasattr(TinyMessageService, "connect")
  assert hasattr(TinyMessageService, "publish")
  assert hasattr(TinyMessageService, "close")
  assert hasattr(TinyMessageService, "run")


def test_tinymessageservicesync_has_expected_methods():
  """Test that TinyMessageServiceSync has expected methods."""
  assert hasattr(TinyMessageServiceSync, "connect")
  assert hasattr(TinyMessageServiceSync, "publish")
  assert hasattr(TinyMessageServiceSync, "consume")
  assert hasattr(TinyMessageServiceSync, "close")
