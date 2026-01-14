"""RabbitMQ messaging services for asynchronous and synchronous communication.

This module provides two RabbitMQ client implementations for the TinyAI microservices
platform: TinyMessageService for event-driven async messaging and TinyMessageServiceSync
for blocking synchronous messaging.

Example:
  Async event-driven messaging::

    from tinysdk import TinyMessageService

    def handle_message(msg: dict):
        print(f"Received: {msg}")

    queue_settings = [("my-queue", handle_message)]
    msg_service = TinyMessageService(queue_settings=queue_settings)
    msg_service.run()

  Sync blocking messaging::

    from tinysdk import TinyMessageServiceSync

    msg_service = TinyMessageServiceSync()
    msg_service.connect()
    msg_service.publish("my-queue", {"data": "hello"})
    msg_service.close()
"""

import json
import logging
import os
from typing import Any, Callable, Dict, List, Tuple, Union

import pika
import pika.adapters.blocking_connection
from pika.adapters.select_connection import SelectConnection
from pika.channel import Channel
from pika.connection import Connection
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker
from pika.spec import Basic, BasicProperties

from tinysdk.utils.decorators import retry

logger = logging.getLogger(__name__)


class TinyMessageService:
  """Async (event-driven) RabbitMQ message service using SelectConnection.

  TinyMessageService provides an asynchronous, event-driven RabbitMQ client using
  pika's SelectConnection. It handles automatic reconnection, fair dispatch, and
  message consumption via callback functions. Best suited for long-running services
  that need to process messages asynchronously.

  Attributes:
    host (str): RabbitMQ server hostname
    port (int): RabbitMQ server port
    user (str): RabbitMQ username
    password (str): RabbitMQ password
    connection (SelectConnection): Active RabbitMQ connection
    channel (Channel): Active RabbitMQ channel
    queue_settings (List[Tuple[str, Callable]]): List of (queue_name, callback) tuples

  Example:
    >>> def process_task(msg: dict):
    ...     print(f"Processing: {msg}")
    >>>
    >>> queue_settings = [("tasks", process_task)]
    >>> msg_service = TinyMessageService(queue_settings=queue_settings)
    >>> msg_service.run()  # Starts IOLoop
  """

  def __init__(
    self,
    queue_settings: List[Tuple[str, Callable[[Dict[str, Any]], None]]],
    host: str = None,
    port: int = None,
    user: str = None,
    password: str = None,
  ):
    """Initialize TinyMessageService with RabbitMQ connection settings.

    Args:
      queue_settings (List[Tuple[str, Callable]]): List of (queue_name, callback) tuples
        for automatic queue consumption. Each callback receives a dict message.
      host (str, optional): RabbitMQ server hostname. Defaults to RABBITMQ_HOST env var.
      port (int, optional): RabbitMQ server port. Defaults to RABBITMQ_PORT env var (5672).
      user (str, optional): RabbitMQ username. Defaults to RABBITMQ_USER env var.
      password (str, optional): RabbitMQ password. Defaults to RABBITMQ_PASS env var.

    Raises:
      AssertionError: If host, port, user, or password not provided via parameters or environment variables.

    Environment Variables:
      RABBITMQ_HOST: RabbitMQ server hostname (e.g., rabbitmq-server)
      RABBITMQ_PORT: RabbitMQ server port (default: 5672)
      RABBITMQ_USER: RabbitMQ username
      RABBITMQ_PASS: RabbitMQ password
    """
    self.host: str = host or os.getenv("RABBITMQ_HOST")
    self.port: int = port or int(os.getenv("RABBITMQ_PORT", "5672"))
    self.user: str = user or os.getenv("RABBITMQ_USER")
    self.password: str = password or os.getenv("RABBITMQ_PASS")
    assert self.host and self.port, "RabbitMQ host and port must be provided via parameters or environment variables"
    assert self.user and self.password, "RabbitMQ username and password must be provided via parameters or environment variables"
    self.connection: Union[SelectConnection, None] = None
    self.channel: Union[Channel, None] = None
    self.queue_settings: List[Tuple[str, Callable[[Dict[str, Any]], None]]] = queue_settings
    self._closing: bool = False

  @retry(exceptions=(AMQPConnectionError,), tries=5, delay=5, backoff=1, jitter=(1, 3), logger=logger)
  def connect(self) -> None:
    """Establishes connection to RabbitMQ server with automatic retry.

    Creates a SelectConnection with configured credentials and heartbeat settings.
    Retries up to 5 times with exponential backoff on connection errors.
    """
    if self.connection is None or not self.connection.is_open:
      credentials = pika.PlainCredentials(self.user, self.password)
      params: pika.ConnectionParameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials, heartbeat=600)
      self.connection = SelectConnection(params, on_open_callback=self.on_open)

  def on_open(self, connection: Connection) -> None:
    """Callback when connection is successfully opened.

    Args:
      connection (Connection): The opened RabbitMQ connection
    """
    logger.info("Connection opened")
    connection.channel(on_open_callback=self.on_channel_open)

  def on_channel_open(self, channel: Channel) -> None:
    """Callback when channel is successfully opened.

    Sets up QoS (fair dispatch) and initializes all queues from queue_settings.

    Args:
      channel (Channel): The opened RabbitMQ channel
    """
    logger.info("Channel opened")
    self.channel = channel
    channel.add_on_close_callback(self.on_channel_closed)
    channel.basic_qos(prefetch_count=1)  # Fair dispatch
    for queue, callback in self.queue_settings:
      self.setup_queue(queue, callback)

  def setup_queue(self, queue: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    logger.info(f"Declaring queue {queue}")
    assert self.channel is not None, "Channel not initialized"
    self.channel.queue_declare(queue=queue, durable=True, callback=lambda _: self.on_queue_declareok(queue, callback))

  def on_queue_declareok(self, queue: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    logger.info(f"Queue {queue} declared")
    assert self.channel is not None, "Channel not initialized"
    self.channel.basic_consume(
      queue=queue, on_message_callback=lambda ch, method, properties, body: self.message_handler(ch, method, properties, body, callback)
    )
    logger.info(f"Started consuming from queue: {queue}")

  def message_handler(
    self, ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes, callback: Callable[[Dict[str, Any]], None]
  ) -> None:
    try:
      callback(json.loads(body))
    except Exception as e:
      logger.error(f"Error processing message: {str(e)}")
    finally:
      ch.basic_ack(delivery_tag=method.delivery_tag)

  def on_channel_closed(self, channel: Channel, reason: Exception) -> None:
    logger.warning(f"Channel {channel} was closed: {reason}")
    self.channel = None
    if not self._closing:
      self.reconnect()

  def reconnect(self) -> None:
    logger.info("Attempting to reconnect...")
    assert self.connection is not None, "Connection not initialized"
    self.connection.ioloop.call_later(5, self.connect)

  @retry(exceptions=(AMQPConnectionError, ChannelClosedByBroker), tries=5, delay=5, backoff=1, jitter=(1, 3), logger=logger)
  def publish(self, queue: str, msg: Dict[str, Any]) -> None:
    """Publishes a message to a RabbitMQ queue with automatic retry.

    Messages are published with persistent delivery mode (delivery_mode=2).
    Retries up to 5 times with exponential backoff on connection/channel errors.

    Args:
      queue (str): The queue name to publish to
      msg (Dict[str, Any]): The message dictionary (will be JSON-encoded)

    Raises:
      AMQPConnectionError: If channel is not available after retries
    """
    if self.channel is None or not self.channel.is_open:
      raise AMQPConnectionError("Channel not available")
    self.channel.basic_publish(exchange="", routing_key=queue, body=json.dumps(msg).encode("utf-8"), properties=BasicProperties(delivery_mode=2))
    logger.info(f"Published message to queue: {queue}")

  def close(self) -> None:
    """Closes the RabbitMQ connection gracefully."""
    self._closing = True
    if self.connection and self.connection.is_open:
      logger.info("Closing connection")
      self.connection.close()

  def run(self) -> None:
    """Starts the IOLoop to begin processing messages.

    This method blocks and runs the event loop. It will automatically reconnect
    on failures and terminate the container (os._exit(1)) on critical errors for
    Kubernetes to restart the pod.

    Raises:
      SystemExit: Exits with code 1 on critical errors
    """
    try:
      self.connect()
      assert self.connection is not None, "Connection not initialized"
      self.connection.ioloop.start()
    except Exception as e:
      logger.error(f"Error running the service: {str(e)}")
      # Kill the container
      logger.critical("Terminating the container for Kubernetes to restart")
      os._exit(1)  # Exit with a non-zero status code


class TinyMessageServiceSync:
  """Sync (blocking) RabbitMQ message service using BlockingConnection.

  TinyMessageServiceSync provides a synchronous, blocking RabbitMQ client using
  pika's BlockingConnection. It's designed for simple publish/consume operations
  where event-driven async processing is not needed. Best suited for scripts,
  simple workers, or services that need direct control over message flow.

  Attributes:
    host (str): RabbitMQ server hostname
    port (int): RabbitMQ server port
    user (str): RabbitMQ username
    password (str): RabbitMQ password
    connection (BlockingConnection): Active RabbitMQ connection
    channel (BlockingChannel): Active RabbitMQ channel

  Example:
    >>> msg_service = TinyMessageServiceSync()
    >>> msg_service.connect()
    >>>
    >>> # Publish a message
    >>> msg_service.publish("my-queue", {"task": "process"})
    >>>
    >>> # Consume messages
    >>> def callback(msg: dict):
    ...     print(f"Received: {msg}")
    >>> msg_service.consume("my-queue", callback)
    >>>
    >>> msg_service.close()
  """

  def __init__(self, host: str = None, port: int = None, user: str = None, password: str = None):
    """Initialize TinyMessageServiceSync with RabbitMQ connection settings.

    Args:
      host (str, optional): RabbitMQ server hostname. Defaults to RABBITMQ_HOST env var.
      port (int, optional): RabbitMQ server port. Defaults to RABBITMQ_PORT env var (5672).
      user (str, optional): RabbitMQ username. Defaults to RABBITMQ_USER env var.
      password (str, optional): RabbitMQ password. Defaults to RABBITMQ_PASS env var.

    Raises:
      AssertionError: If host, port, user, or password not provided via parameters or environment variables.

    Environment Variables:
      RABBITMQ_HOST: RabbitMQ server hostname (e.g., rabbitmq-server)
      RABBITMQ_PORT: RabbitMQ server port (default: 5672)
      RABBITMQ_USER: RabbitMQ username
      RABBITMQ_PASS: RabbitMQ password
    """
    self.host: str = host or os.getenv("RABBITMQ_HOST")
    self.port: int = port or int(os.getenv("RABBITMQ_PORT", "5672"))
    self.user: str = user or os.getenv("RABBITMQ_USER")
    self.password: str = password or os.getenv("RABBITMQ_PASS")
    assert self.host and self.port, "RabbitMQ host and port must be provided via parameters or environment variables"
    assert self.user and self.password, "RabbitMQ username and password must be provided via parameters or environment variables"
    self.connection: Union[pika.BlockingConnection, None] = None
    self.channel: Union[pika.adapters.blocking_connection.BlockingChannel, None] = None

  @retry(exceptions=(AMQPConnectionError,), tries=5, delay=5, backoff=1, jitter=(1, 3), logger=logger)
  def connect(self) -> None:
    """Establishes a blocking connection to RabbitMQ server with automatic retry.

    Creates a BlockingConnection with configured credentials, heartbeat settings,
    and fair dispatch QoS. Retries up to 5 times with exponential backoff on
    connection errors.
    """
    if self.connection is None or not self.connection.is_open:
      credentials = pika.PlainCredentials(self.user, self.password)
      params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials, heartbeat=600)
      self.connection = pika.BlockingConnection(params)
      self.channel = self.connection.channel()
      self.channel.basic_qos(prefetch_count=1)  # fair dispatch
      logger.info("Connected to RabbitMQ")

  @retry(exceptions=(AMQPConnectionError,), tries=5, delay=5, backoff=1, jitter=(1, 3), logger=logger)
  def ensure_connection(self):
    """Ensures an active connection exists, reconnecting if necessary.

    Checks if channel is open and reconnects if not. Used internally before
    publish operations to maintain connection reliability.
    """
    if self.channel is None or not self.channel.is_open:
      self.connect()

  @retry(exceptions=(AMQPConnectionError, ChannelClosedByBroker), tries=5, delay=5, backoff=1, jitter=(1, 3), logger=logger)
  def publish(self, queue: str, msg: Dict[str, Any]) -> None:
    """Publishes a message to a RabbitMQ queue with automatic retry.

    Messages are published with persistent delivery mode (delivery_mode=2).
    Automatically ensures connection before publishing. Retries up to 5 times
    with exponential backoff on connection/channel errors.

    Args:
      queue (str): The queue name to publish to
      msg (Dict[str, Any]): The message dictionary (will be JSON-encoded)
    """
    self.ensure_connection()
    assert self.channel, "Channel not initialized"
    self.channel.basic_publish(exchange="", routing_key=queue, body=json.dumps(msg).encode("utf-8"), properties=pika.BasicProperties(delivery_mode=2))
    logger.info(f"Published message to queue: {queue}")

  def close(self) -> None:
    """Closes the RabbitMQ connection gracefully."""
    if self.connection and self.connection.is_open:
      self.connection.close()
      logger.info("Closed RabbitMQ connection")

  def consume(self, queue: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    """Starts consuming messages from a queue (blocking call).

    Declares the queue as durable and begins consuming messages. Each message
    is passed to the callback function after JSON decoding. Messages are
    acknowledged after successful processing. This method blocks until interrupted.

    Args:
      queue (str): The queue name to consume from
      callback (Callable[[Dict[str, Any]], None]): Function to call with each message
    """
    self.ensure_connection()
    assert self.channel, "Channel not initialized"
    self.channel.queue_declare(queue=queue, durable=True)

    def message_handler(ch, method, properties, body):
      try:
        callback(json.loads(body))
      except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
      finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

    self.channel.basic_consume(queue=queue, on_message_callback=message_handler)
    logger.info(f"Started consuming from queue: {queue}")
    self.channel.start_consuming()
