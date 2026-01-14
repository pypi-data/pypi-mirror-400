"""Tests for TinyDBService."""

import pytest

from tinysdk import TinyDBService


def test_tinydbservice_import():
  """Test that TinyDBService can be imported."""
  assert TinyDBService is not None


def test_tinydbservice_initialization_with_params(mongodb_credentials):
  """Test TinyDBService initialization with explicit parameters."""
  db = TinyDBService(**mongodb_credentials)
  assert db.db_link == mongodb_credentials["db_link"]
  assert db.db_name == mongodb_credentials["db_name"]


def test_tinydbservice_initialization_without_params_fails():
  """Test that TinyDBService initialization fails without credentials."""
  with pytest.raises(AssertionError):
    TinyDBService()


def test_tinydbservice_has_crud_methods():
  """Test that TinyDBService has expected CRUD methods."""
  assert hasattr(TinyDBService, "create")
  assert hasattr(TinyDBService, "read")
  assert hasattr(TinyDBService, "update")
  assert hasattr(TinyDBService, "delete")
  assert hasattr(TinyDBService, "create_multiple")
  assert hasattr(TinyDBService, "exists")
