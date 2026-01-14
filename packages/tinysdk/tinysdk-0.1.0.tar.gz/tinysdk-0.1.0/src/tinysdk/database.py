"""MongoDB database service with CRUD operations and index management.

This module provides TinyDBService, a high-level MongoDB client for the TinyAI
microservices platform. It handles common database operations with automatic
index management and ObjectId conversion.

Example:
  Basic usage with environment variables::

    from tinysdk import TinyDBService

    db = TinyDBService()
    result = db.create({
        "collection": "users",
        "document": {"name": "John", "email": "john@example.com"}
    })
"""

import logging
import os
from typing import Any, Dict, List

from bson.objectid import ObjectId
from pymongo import ASCENDING, MongoClient

from tinysdk.utils.decorators import exception_logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default index configuration for common collections
DEFAULT_INDEX_CONFIG = {
  "users": [[("email", ASCENDING), {"unique": True}]],
  "documents": [[("fileName", ASCENDING), {"unique": True}]],
}


class TinyDBService:
  """MongoDB service for CRUD operations with automatic index management.

  TinyDBService provides a high-level interface for MongoDB operations including
  create, read, update, delete, and bulk operations. It automatically manages
  indexes based on configuration and handles ObjectId conversions.

  Attributes:
    db_link (str): MongoDB connection string
    db_name (str): Database name
    client (MongoClient): Active MongoDB client connection
    db: MongoDB database instance
    index_config (Dict[str, List]): Index configuration for collections

  Example:
    >>> # Using environment variables
    >>> db = TinyDBService()
    >>>
    >>> # Or explicit parameters
    >>> db = TinyDBService(
    ...     db_link="mongodb://localhost:27017",
    ...     db_name="mydb"
    ... )
    >>>
    >>> # Create a document
    >>> result = db.create({
    ...     "collection": "users",
    ...     "document": {"name": "John", "email": "john@example.com"}
    ... })
  """

  @exception_logger
  def __init__(self, db_link: str = None, db_name: str = None, index_config: Dict[str, List] = None) -> None:
    """Initialize TinyDBService with MongoDB connection.

    Args:
      db_link (str, optional): MongoDB connection string. Defaults to DB_LINK env var.
      db_name (str, optional): Database name. Defaults to DB_NAME env var.
      index_config (Dict[str, List], optional): Custom index configuration to merge with defaults.

    Raises:
      AssertionError: If db_link or db_name not provided via parameters or environment variables.

    Environment Variables:
      DB_LINK: MongoDB connection string (e.g., mongodb://mongo-server:27017)
      DB_NAME: Database name (e.g., tinyDatabase)
    """
    self.db_link = db_link or os.getenv("DB_LINK")
    self.db_name = db_name or os.getenv("DB_NAME")
    assert self.db_link, "DB_LINK must be provided via parameter or environment variable"
    assert self.db_name, "DB_NAME must be provided via parameter or environment variable"

    self.client: MongoClient = MongoClient(self.db_link)
    self.db = self.client.get_database(self.db_name)

    # Initialize index configuration
    self.index_config = DEFAULT_INDEX_CONFIG.copy()
    if index_config:
      self.index_config.update(index_config)

  @exception_logger
  def create(self, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Inserts a new document into the specified collection.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name and document to insert.

    Returns:
        Dict[str, str]: Status and Document_ID or an error message.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    new_document = data.get("document")
    if new_document is None:
      raise ValueError("No document provided")
    if new_document.get("_id"):
      new_document["_id"] = ObjectId(new_document.get("_id"))
    response = collection.insert_one(new_document)
    return {"Status": "Success", "Document_ID": str(response.inserted_id)}

  @exception_logger
  def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves documents from the specified collection based on filters and options.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name, filter, sort, and paging information.

    Returns:
        Dict[str, Any]: Status, list of documents, and total count or an error message.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    # Filter
    search_filter = self._convert_filter_id(data.get("filter", {}))
    documents = collection.find(search_filter)
    # Sorting
    sort = data.get("sort", {})
    field, direction = sort.get("field"), sort.get("direction")
    if field and direction:
      documents = documents.sort(field, direction)
    # Paging
    paging = data.get("paging", {})
    page, limit = paging.get("page", 0), paging.get("limit", 0)
    if limit > 0:
      documents = documents.skip(page * limit).limit(limit)
    # Count and conversion
    total_count = collection.count_documents(search_filter)
    output = [{**doc, "_id": str(doc.get("_id"))} for doc in documents]
    # Return both the documents and the total count
    return {"Status": "Success", "documents": output, "total_count": total_count}

  @exception_logger
  def update(self, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Updates documents in the specified collection based on the filter.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name, filter, and update data.

    Returns:
        Dict[str, str]: Status and update result or an error message.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    search_filter = self._convert_filter_id(data.get("filter", {}))
    response = collection.update_many(search_filter, data.get("data"))
    msg = f"Successfully updated {response.modified_count} records." if response.modified_count > 0 else "No documents updated."
    output = {"Status": "Success", "Message": msg}
    return output

  @exception_logger
  def delete(self, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Deletes documents from the specified collection based on the filter.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name and filter.

    Returns:
        Dict[str, str]: Status and delete result or an error message.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    response = collection.delete_many(data.get("filter", {}))
    msg = f"Successfully deleted {response.deleted_count} records." if response.deleted_count > 0 else "No documents deleted."
    output = {"Status": "Success", "Message": msg}
    return output

  @exception_logger
  def _init_index(self, collection_name: str) -> None:
    """
    Initializes indexes for the specified collection based on the index configuration.

    Args:
        collection_name (str): The name of the collection for which to create indexes.
    """
    assert collection_name is not None, "Collection name cannot be None"
    collection = self.db.get_collection(collection_name)
    # Iterate through the indexes for this collection
    for index in self.index_config.get(collection_name, []):
      # The index specification (a list) can have additional parameters
      fields = index[:-1] if isinstance(index[-1], dict) else index
      options = index[-1] if isinstance(index[-1], dict) else {}
      # Create the index
      collection.create_index(fields, **options)

  @exception_logger
  def _convert_filter_id(self, filter: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts string IDs in the filter to ObjectId.

    Args:
    filter (Dict[str, Any]): Dictionary containing filter criteria.

    Returns:
    Dict[str, Any]: Filter with ObjectId values.
    """
    id = filter.get("_id", None)
    if isinstance(id, str):
      filter["_id"] = ObjectId(id)
    elif isinstance(id, dict) and "$in" in id:
      filter["_id"]["$in"] = [ObjectId(id_str) for id_str in id.get("$in")]
    return filter

  @exception_logger
  def create_multiple(self, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Inserts multiple documents into the specified collection.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name and documents to insert.

    Returns:
        Dict[str, str]: Status or an error message.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    new_documents = data.get("documents")
    if new_documents is None:
      raise ValueError("No documents provided")
    result = collection.insert_many(new_documents)
    return {"Status": "Success", "result": result}

  @exception_logger
  def exists(self, data: Dict[str, Any]) -> bool:
    """
    Checks if a document exists in the specified collection based on the filter.

    Args:
        data (Dict[str, Any]): Dictionary containing the collection name and filter.

    Returns:
        bool: True if a document exists, False otherwise.
    """
    self._init_index(data.get("collection"))
    collection = self.db.get_collection(data.get("collection"))
    search_filter = self._convert_filter_id(data.get("filter", {}))
    return collection.count_documents(search_filter) > 0
