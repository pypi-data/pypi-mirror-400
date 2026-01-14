"""MinIO/S3-compatible object storage handler with file and folder operations.

This module provides TinyStorageHandler, a high-level MinIO client for the TinyAI
microservices platform. It handles file uploads, downloads, deletions, and folder
operations with automatic connection management.

Example:
  Basic usage with environment variables::

    from tinysdk import TinyStorageHandler

    storage = TinyStorageHandler()

    # Upload a file
    with open("document.pdf", "rb") as f:
      buffer = io.BytesIO(f.read())
      storage.upload_file("my-bucket", "document.pdf", buffer, buffer.getbuffer().nbytes)

    # Download a file
    file_buffer, object_name = storage.download_file("my-bucket", "document.pdf")
"""

import io
import logging
import os
from typing import List, Tuple, Union

from minio import Minio
from minio.error import S3Error

from tinysdk.utils.decorators import exception_logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TinyStorageHandler:
  """MinIO/S3 storage handler for file and folder operations.

  TinyStorageHandler provides a high-level interface for MinIO/S3 object storage
  operations including upload, download, delete for both files and folders. It
  supports custom HTTP clients for advanced connection pooling configurations.

  Attributes:
    endpoint (str): MinIO server endpoint (e.g., "minio-server:9000")
    access_key (str): MinIO access key
    secret_key (str): MinIO secret key
    client (Minio): Active MinIO client connection

  Example:
    >>> # Using environment variables
    >>> storage = TinyStorageHandler()
    >>>
    >>> # Or explicit parameters
    >>> storage = TinyStorageHandler(
    ...     endpoint="minio-server:9000",
    ...     access_key="myaccesskey",
    ...     secret_key="mysecretkey"
    ... )
    >>>
    >>> # Upload a file
    >>> with open("file.pdf", "rb") as f:
    ...     buffer = io.BytesIO(f.read())
    ...     storage.upload_file("bucket", "file.pdf", buffer, buffer.getbuffer().nbytes)
  """

  def __init__(self, endpoint: str = None, access_key: str = None, secret_key: str = None, secure: bool = False, http_client=None):
    """Initialize TinyStorageHandler with MinIO connection.

    Args:
      endpoint (str, optional): MinIO server endpoint. Defaults to MINIO_ENDPOINT env var.
      access_key (str, optional): MinIO access key. Defaults to MINIO_ACCESSKEY env var.
      secret_key (str, optional): MinIO secret key. Defaults to MINIO_SECRETKEY env var.
      secure (bool, optional): Use HTTPS for connection. Defaults to False.
      http_client (urllib3.PoolManager, optional): Custom HTTP client with connection pooling.

    Raises:
      AssertionError: If endpoint, access_key, or secret_key not provided via parameters or environment variables.

    Environment Variables:
      MINIO_ENDPOINT: MinIO server endpoint (e.g., minio-server:9000)
      MINIO_ACCESSKEY: MinIO access key
      MINIO_SECRETKEY: MinIO secret key
    """
    self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT")
    self.access_key = access_key or os.getenv("MINIO_ACCESSKEY")
    self.secret_key = secret_key or os.getenv("MINIO_SECRETKEY")
    assert self.endpoint and self.access_key and self.secret_key, "MinIO credentials must be provided via parameters or environment variables"
    self.client = Minio(self.endpoint, access_key=self.access_key, secret_key=self.secret_key, secure=secure, http_client=http_client)

  @exception_logger
  def upload_result(self, bucket_name: str, file_path: str) -> None:
    """Uploads a local file to MinIO storage (convenience method).

    Args:
      bucket_name (str): The name of the destination bucket
      file_path (str): Local filesystem path to the file to upload
    """
    with open(file_path, "rb") as f:
      file_buffer = io.BytesIO(f.read())
      self.upload_file(bucket_name, file_path, file_buffer, file_buffer.getbuffer().nbytes)
    logger.info(f"Result file '{file_path}' successfully uploaded to '{bucket_name}'.")

  @exception_logger
  def upload_file(self, bucket_name: str, object_name: str, file_buffer: io.BytesIO, file_size: int, dest_path: Union[None, str] = None) -> None:
    """Uploads a file buffer to MinIO storage.

    Args:
      bucket_name (str): The name of the destination bucket
      object_name (str): The name/path for the object in MinIO
      file_buffer (io.BytesIO): The file content as a BytesIO buffer
      file_size (int): Size of the file in bytes
      dest_path (str, optional): Destination folder path within the bucket
    """
    object_name = f"{dest_path}/{object_name}" if dest_path is not None else object_name
    self.client.put_object(bucket_name, object_name, file_buffer, file_size)
    logger.info(f"'{object_name}' successfully uploaded to '{bucket_name}' from buffer.")

  @exception_logger
  def upload_folder(self, bucket_name: str, folder_path: str, dest_path: Union[None, str] = None) -> None:
    """Uploads an entire folder recursively to MinIO storage.

    Args:
      bucket_name (str): The name of the destination bucket
      folder_path (str): Local filesystem path to the folder to upload
      dest_path (str, optional): Destination folder path within the bucket
    """
    folder_name = folder_path.split("/")[-1]
    for root, _, files in os.walk(folder_path):
      for file in files:
        file_path = os.path.join(root, file)
        object_name = os.path.relpath(file_path, folder_path)
        if self.object_exists(bucket_name, object_name):
          return
        with open(file_path, "rb") as f:
          file_buffer = io.BytesIO(f.read())
          object_name = f"{dest_path}/{folder_name}/{object_name}" if dest_path is not None else f"{folder_name}/{object_name}"
          self.upload_file(bucket_name, object_name, file_buffer, file_buffer.getbuffer().nbytes)
    logger.info(f"Folder '{folder_path}' successfully uploaded to '{bucket_name}'.")

  @exception_logger
  def delete_file(self, bucket_name: str, object_name: str) -> None:
    """Deletes a file from MinIO storage.

    Args:
      bucket_name (str): The name of the bucket
      object_name (str): The name/path of the object to delete
    """
    self.client.remove_object(bucket_name, object_name)
    logger.info(f"'{object_name}' successfully deleted from '{bucket_name}'.")

  @exception_logger
  def delete_folder(self, bucket_name: str, folder_name: str) -> None:
    """Deletes an entire folder recursively from MinIO storage.

    Args:
      bucket_name (str): The name of the bucket
      folder_name (str): The folder path/prefix to delete recursively
    """
    for obj in self.client.list_objects(bucket_name, prefix=folder_name, recursive=True):
      self.delete_file(bucket_name, obj.object_name)
    logger.info(f"Folder '{folder_name}' successfully deleted from '{bucket_name}'.")

  @exception_logger
  def download_file(self, bucket_name: str, object_name: str, download_path: Union[None, str] = None) -> Tuple[io.BytesIO, str]:
    """Downloads a file from MinIO storage.

    Args:
      bucket_name (str): The name of the bucket
      object_name (str): The name/path of the object in the bucket
      download_path (str, optional): If provided, saves file to this path on disk

    Returns:
      Tuple[io.BytesIO, str]: A tuple containing the file buffer and the object name
    """
    response = self.client.get_object(bucket_name, object_name)
    try:
      file_buffer = io.BytesIO(response.read())
      logger.info(f"'{object_name}' successfully downloaded from '{bucket_name}' to buffer.")
      if download_path is not None:
        file_path = os.path.join(download_path or "", os.path.join(os.path.basename(os.path.dirname(object_name)), os.path.basename(object_name)))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
          f.write(file_buffer.getvalue())
        logger.info(f"'{object_name}' successfully downloaded from '{bucket_name}' to '{download_path}'.")
      return file_buffer, object_name
    finally:
      response.close()
      response.release_conn()

  @exception_logger
  def download_folder(self, bucket_name: str, folder_name: str, download_path: Union[None, str] = None) -> None:
    """Downloads an entire folder recursively from MinIO storage.

    Args:
      bucket_name (str): The name of the bucket
      folder_name (str): The folder path/prefix to download recursively
      download_path (str, optional): Local filesystem path to save the folder
    """
    for obj in self.client.list_objects(bucket_name, prefix=folder_name, recursive=True):
      file_buffer, _ = self.download_file(bucket_name, obj.object_name)
      file_path = os.path.join(
        download_path or "", os.path.join(os.path.basename(os.path.dirname(obj.object_name)), os.path.basename(obj.object_name))
      )
      os.makedirs(os.path.dirname(file_path), exist_ok=True)
      with open(file_path, "wb") as f:
        f.write(file_buffer.getvalue())
    logger.info(f"Folder '{folder_name}' successfully downloaded from '{bucket_name}' to '{download_path}'.")

  @exception_logger
  def list_objects(self, bucket_name: str, prefix=None) -> List[Union[str, None]]:
    """Lists all objects in a bucket, optionally filtered by prefix.

    Args:
      bucket_name (str): The name of the bucket
      prefix (str, optional): Filter objects by this prefix/folder path

    Returns:
      List[Union[str, None]]: List of object names in the bucket
    """
    return [obj.object_name for obj in self.client.list_objects(bucket_name, prefix=prefix, recursive=True)]

  @exception_logger
  def object_exists(self, bucket: str, object_name: str) -> bool:
    """Checks if an object exists in a bucket.

    Args:
      bucket (str): The name of the bucket
      object_name (str): The name/path of the object to check

    Returns:
      bool: True if the object exists, False otherwise
    """
    try:
      self.client.stat_object(bucket, object_name)
      return True
    except S3Error:
      return False

  @exception_logger
  def close(self):
    """Closes the MinIO client connection and clears the HTTP connection pool."""
    if hasattr(self, "client"):
      self.client._http.clear()
      logger.info("MinIO client connection closed.")
