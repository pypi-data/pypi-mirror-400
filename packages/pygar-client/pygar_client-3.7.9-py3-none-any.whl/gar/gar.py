"""
GAR Client Module

See GARClient documentation for more details.
"""

import asyncio
import getpass
import logging
import os
import ssl
import threading
import time
import uuid
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple, Union

import websockets
from msgspec import DecodeError, json
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed

import __main__


def our_enc_hook(obj: Any) -> Any:
    """ " Convert enum instances to their string names for JSON serialization."""
    if isinstance(obj, Enum):
        return obj.name

    # msgspec.json apparently checks for exact type, rather than isinstance
    # convert derived primitives so they don't format as json strings

    if isinstance(obj, float):
        return float(obj)

    if isinstance(obj, int):
        return int(obj)

    return str(obj)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
class GARClient:
    """
    A client implementation for the Generic Active Records (GAR) protocol using WebSockets.

    See trsgar.py for example usage.

    The GARClient class provides a Python interface for connecting to a GAR server
    using WebSockets as the transport layer. It handles the protocol details including
    message serialization, heartbeat management, topic and key enumeration, record
    updates, and subscription management.

    The client maintains separate mappings for server-assigned and client-assigned
    topic and key IDs, allowing for independent enumeration on both sides. It provides
    methods for subscribing to data, publishing records, and registering handlers for
    various message types.

    Key features:
    - Automatic heartbeat management to maintain connection
    - Support for topic and key int <-> string introductions
    - Record creation, updating, and deletion
    - Subscription management with filtering options
    - Customizable message handlers for all protocol message types
    - Thread-safe message sending
    - Automatic reconnection on WebSocket connection loss

    See the full documentation at https://trinityriversystems.com/docs/ for detailed
    protocol specifications and usage instructions.
    """

    _initial_grace_period: bool
    _initial_grace_deadline: float

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ws_endpoint: str,
        working_namespace: str | None = None,
        heartbeat_timeout_interval: int = 4000,
        allow_self_signed_certificate: bool = False,
        ws_buffer_size: int = 2097152,
    ) -> None:
        """
        Initialize the GAR (Generic Active Records) client.

        Creates a new GAR client instance that connects to a GAR server using WebSockets.
        It sets up internal data structures for tracking topics, keys, and message handlers,
        and initializes the heartbeat mechanism for maintaining the connection.

        Args:
            ws_endpoint: WebSocket endpoint string in the format "ws://address:port"
                         (e.g., "ws://localhost:8765") where the GAR server is listening.
            user: Client username string used for identification and authentication
                  with the server. This is included in the socket identity.
            heartbeat_timeout_interval: Timeout in milliseconds for checking heatbeats. Default is 4000ms (4 seconds).

        Returns:
            None

        Note:
            The client is not started automatically after initialization.
            Call the start() method to begin communication with the server.
            start() will run the IO loop until stop() is called.
            Use threading.Thread(target=gar_client.start) to run in the background.
        """
        self.ws_endpoint = ws_endpoint
        self.websocket: Optional[ClientConnection] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.connected = False
        self.encoder = json.Encoder(enc_hook=our_enc_hook)
        self.decoder = json.Decoder(float_hook=Decimal)
        self.reconnect_delay = 5.0  # Seconds to wait before reconnecting

        self.pid = os.getpid()
        self.logger = logging.getLogger(__name__)

        self.user = os.getenv("GAR_USERNAME") or os.environ.get(
            "USER", getpass.getuser()
        )
        self.application = os.path.basename(getattr(__main__, "__file__", "unknown-py"))
        self.working_namespace = working_namespace
        self.timeout_scale = float(os.getenv("TRS_TIMEOUT_SCALE", "1"))
        self.scaled_heartbeat_timeout_interval = heartbeat_timeout_interval / 1000.0
        if self.timeout_scale != 1.0:
            self.scaled_heartbeat_timeout_interval *= self.timeout_scale
        self.version = 650707

        self._key_lock = threading.Lock()
        self._topic_lock = threading.Lock()

        # Event to signal first heartbeat receipt after an Introduction
        # Must be created BEFORE clear_connection_state() which may clear it
        self.first_heartbeat_received: threading.Event = threading.Event()

        self.clear_connection_state()

        self.running = False
        self.heartbeat_thread: Optional[threading.Thread] = None

        self.message_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

        self.last_heartbeat_time = time.time()

        self.heartbeat_timeout_callback: Optional[Callable[[], None]] = None
        self.stopped_callback: Optional[Callable[[], None]] = None

        self.allow_self_signed_certificate = allow_self_signed_certificate
        self.exit_code = 0

        logging.basicConfig(level=logging.INFO)
        self.register_default_handlers()

        # Asyncio event loop for WebSocket operations
        self.loop = asyncio.new_event_loop()

        self.active_subscription_group = 0

        self.ws_buffer_size = ws_buffer_size

        # route_query per-thread subscription group counters
        self._route_query_counter_lock = threading.Lock()
        self._route_query_tid_counters: dict[int, int] = {}
        self._route_query_tid_counter: int = 0

    def clear_connection_state(self) -> None:
        """
        Reset all connection-related state:
        server/client topic/key mappings, counters, grace flags, and records.
        """
        with self._key_lock:
            with self._topic_lock:
                # Server assigned topic/key <-> name mappings
                self.server_topic_id_to_name: Dict[int, str] = {}
                self.server_topic_name_to_id: Dict[str, int] = {}
                self.server_key_id_to_name: Dict[int, str] = {}
                self.server_key_name_to_id: Dict[str, int] = {}

                # Client assigned topic/key counters and name <-> ID maps
                self.local_topic_counter = 1
                self.local_key_counter = 1
                self.local_topic_map: Dict[str, int] = {}
                self.local_key_map: Dict[str, int] = {}

                # Heartbeat grace period flags
                self._initial_grace_period = False
                self._initial_grace_deadline = 0.0

                # Cached records
                self.record_map: Dict[Tuple[int, int], Any] = {}

                # Reset first heartbeat event for a new connection state
                if self.first_heartbeat_received.is_set():
                    self.logger.debug(
                        "%s Clearing first heartbeat event",
                        self._log_prefix(),
                    )
                self.first_heartbeat_received.clear()

    def _log_prefix(self) -> str:
        """Return a prefix string identifying this client for logging."""
        return f"[{self.application}@{self.user}]"

    async def connect(self, open_timeout: int = 30) -> None:
        """Establish WebSocket connection with reconnection logic, using GAR subprotocol."""
        # Before attempting a new connection, clear any previous state
        self.clear_connection_state()

        scaled_open_timeout = float(open_timeout)
        if self.timeout_scale != 1.0:
            scaled_open_timeout *= self.timeout_scale

        while self.running and not self.connected:
            try:
                connect_kwargs: Dict[str, Any] = {"subprotocols": ["gar-protocol"]}
                if self.ws_endpoint.lower().startswith("wss://"):
                    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    if self.allow_self_signed_certificate:
                        ssl_ctx.check_hostname = False
                        ssl_ctx.verify_mode = ssl.CERT_NONE
                    connect_kwargs["ssl"] = ssl_ctx

                connect_start = time.time()
                self.logger.info(
                    "%s Connecting to WebSocket server at %s",
                    self._log_prefix(),
                    self.ws_endpoint,
                )

                async with websockets.connect(
                    self.ws_endpoint,
                    max_size=self.ws_buffer_size,
                    open_timeout=scaled_open_timeout,
                    **connect_kwargs,
                    ping_interval=min(
                        60,
                        max(
                            10,
                            self.scaled_heartbeat_timeout_interval / 2,
                        ),
                    ),
                    ping_timeout=max(10, self.scaled_heartbeat_timeout_interval + 1),
                ) as websocket:
                    handshake_elapsed = time.time() - connect_start
                    self.websocket = websocket
                    self.connected = True
                    self.logger.info(
                        "%s WebSocket handshake complete in %.3fs to %s",
                        self._log_prefix(),
                        handshake_elapsed,
                        self.ws_endpoint,
                    )
                    await asyncio.gather(
                        self._send_messages(), self._receive_messages()
                    )
            except (ConnectionClosed, ConnectionRefusedError):
                self.logger.exception(
                    "%s WebSocket connection to %s failed. Reconnecting in %s seconds...",
                    self._log_prefix(),
                    self.ws_endpoint,
                    self.reconnect_delay,
                )
                self.connected = False
                self.websocket = None
                await asyncio.sleep(self.reconnect_delay)

    async def _send_messages(self) -> None:
        """Send messages from the queue to the WebSocket server."""
        while self.connected and (self.running or not self.message_queue.empty()):
            try:
                message = await self.message_queue.get()
                if message is None:
                    break
                if self.websocket:
                    json_message = self.encoder.encode(message).decode()
                    await self.websocket.send(json_message)
                    # self.logger.debug("%s Sent: %s", self._log_prefix(), json_message)
                self.message_queue.task_done()
            except ConnectionClosed:
                self.logger.warning(
                    "%s Connection closed while sending.", self._log_prefix()
                )
                self.stop()
                break
            # pylint: disable=broad-exception-caught
        self.connected = False
        self.logger.info("%s Done sending messages.", self._log_prefix())

        # try to clear spurious "RuntimeWarning: coroutine 'Queue.put' was never awaited"
        try:
            self.message_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

    async def _receive_messages(self) -> None:
        """Receive and process messages from the WebSocket server."""
        while self.connected and self.running:
            try:
                if self.websocket:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1)
                    msg = self.decoder.decode(message)
                    self._process_message(msg)
            except asyncio.TimeoutError:
                self.check_heartbeat()
            except ConnectionClosed:
                self.logger.info(
                    "%s Connection closed while receiving.", self._log_prefix()
                )
                self.halt()
                break
            except DecodeError as e:
                self.logger.error("%s Invalid JSON received: %s", self._log_prefix(), e)
                break
        self.stop()
        asyncio.run_coroutine_threadsafe(
            self.message_queue.put(None), self.loop
        )  # Put None into the queue to stop the send loop
        self.logger.info("%s Done receiving messages.", self._log_prefix())

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[Dict[str, Any]], None],
        subscription_group: int = 0,
    ) -> None:
        """Register a callback handler for a specific message type."""
        self.message_handlers[
            (
                f"{message_type} {subscription_group}"
                if subscription_group
                else message_type
            )
        ] = handler

    def register_introduction_handler(
        self, handler: Callable[[int, int, str, Optional[str]], None]
    ) -> None:
        """Handler for Introduction: (version, heartbeat_timeout_interval, user, schema)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(
                value["version"],
                value["heartbeat_timeout_interval"],
                value["user"],
                value.get("schema"),
            )

        self.register_handler("Introduction", wrapper)

    def clear_introduction_handler(self) -> None:
        """Remove the registered introduction handler."""
        self.message_handlers.pop("Introduction", None)

    def register_heartbeat_handler(self, handler: Callable[[int], None]) -> None:
        """Handler for Heartbeat"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["u_milliseconds"])

        self.register_handler("Heartbeat", wrapper)

    def clear_heartbeat_handler(self) -> None:
        """Remove the registered heartbeat handler."""
        self.message_handlers.pop("Heartbeat", None)

    def register_logoff_handler(self, handler: Callable[[], None]) -> None:
        """Handler for Logoff: no arguments"""

        # pylint: disable=unused-argument
        def wrapper(msg: Dict[str, Any]):
            handler()

        self.register_handler("Logoff", wrapper)

    def clear_logoff_handler(self) -> None:
        """Remove the registered logoff handler."""
        self.message_handlers.pop("Logoff", None)

    def register_error_handler(self, handler: Callable[[str], None]) -> None:
        """Handler for Error: (message)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["message"])

        self.register_handler("Error", wrapper)

    def clear_error_handler(self) -> None:
        """Remove the registered error handler."""
        self.message_handlers.pop("Error", None)

    def register_topic_introduction_handler(
        self, handler: Callable[[int, str], None]
    ) -> None:
        """Handler for TopicIntroduction: (topic_id, name)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(value["topic_id"], value["name"])

        self.register_handler("TopicIntroduction", wrapper)

    def clear_topic_introduction_handler(self) -> None:
        """Remove the registered topic introduction handler."""
        self.message_handlers.pop("TopicIntroduction", None)

    def register_key_introduction_handler(
        self,
        handler: Callable[[int, str, Optional[list[str]], Optional[str]], None],
        subscription_group: int = 0,
    ) -> None:
        """Handler for KeyIntroduction: (key_id, name, class_list)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(
                value["key_id"],
                value["name"],
                value.get("class_list"),
                value.get("deleted_class"),
            )

        self.register_handler("KeyIntroduction", wrapper, subscription_group)

    def register_delete_key_handler(
        self, handler: Callable[[int], None], subscription_group: int = 0
    ) -> None:
        """Handler for DeleteKey: (key_id)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["key_id"])

        self.register_handler("DeleteKey", wrapper, subscription_group)

    def register_subscription_status_handler(
        self, handler: Callable[[str, str], None], subscription_group: int = 0
    ) -> None:
        """
        Handler for SubscriptionStatus: (name)
        Callback args are (name, status)
        status can be "Streaming" or "Finished"
        """

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["name"], msg["value"]["status"])

        self.register_handler("SubscriptionStatus", wrapper, subscription_group)

    def clear_subscription_status_handler(self, subscription_group: int = 0) -> None:
        """Remove the registered subscription status handler."""
        key = (
            f"SubscriptionStatus {subscription_group}"
            if subscription_group
            else "SubscriptionStatus"
        )
        self.message_handlers.pop(key, None)

    def register_delete_record_handler(
        self, handler: Callable[[int, int], None], subscription_group: int = 0
    ) -> None:
        """Handler for DeleteRecord: (key_id, topic_id)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["key_id"], msg["value"]["topic_id"])

        self.register_handler("DeleteRecord", wrapper, subscription_group)

    def register_record_update_handler(
        self, handler: Callable[[int, int, Any], None], subscription_group: int = 0
    ) -> None:
        """Handler for JSONRecordUpdate: (key_id, topic_id, value)"""

        def wrapper(msg: Dict[str, Any]):
            record_id = msg["value"]["record_id"]
            handler(record_id["key_id"], record_id["topic_id"], msg["value"]["value"])

        self.register_handler("JSONRecordUpdate", wrapper, subscription_group)

    def register_batch_update_handler(
        self, handler: Callable[[dict, int], None], subscription_group: int = 0
    ) -> None:
        """
        Handler for BatchUpdate: (batch_data, subscription_group)
        If a batch handler is registered it is expected to process all the updates in the batch.
        If no batch handler is registered, individual key introductions and record updates will be fanned out to their respective handlers.
        """

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"], subscription_group)

        self.register_handler("BatchUpdate", wrapper, subscription_group)

    def register_heartbeat_timeout_handler(self, handler: Callable[[], None]) -> None:
        """Register a callback to handle heartbeat timeout events."""
        self.heartbeat_timeout_callback = handler

    def clear_heartbeat_timeout_handler(self) -> None:
        """Remove the registered heartbeat timeout handler."""
        self.heartbeat_timeout_callback = None

    def register_stopped_handler(self, handler: Callable[[], None]) -> None:
        """Register a callback to handle client stopped events."""
        self.stopped_callback = handler

    def clear_stopped_handler(self) -> None:
        """Remove the registered stopped handler."""
        self.stopped_callback = None

    def register_default_handlers(self) -> None:
        """Register default logging handlers for all message types."""
        self.register_introduction_handler(
            lambda version, interval, user, schema: self.logger.info(
                "%s Connected to server: %s", self._log_prefix(), user
            )
        )
        self.register_heartbeat_handler(
            lambda ms: self.logger.debug(
                "%s Heartbeat received %dms", self._log_prefix(), ms
            )
        )
        self.register_logoff_handler(
            lambda: self.logger.info("%s Logoff received", self._log_prefix())
        )
        self.register_topic_introduction_handler(
            lambda topic_id, name: self.logger.debug(
                "%s New server topic: %s (Server ID: %d)",
                self._log_prefix(),
                name,
                topic_id,
            )
        )
        self.register_key_introduction_handler(
            lambda key_id, name, class_list, deleted_class: self.logger.debug(
                "%s Key: %s : %s/-%s (Server ID: %d)",
                self._log_prefix(),
                name,
                class_list,
                deleted_class if deleted_class else "",
                key_id,
            )
        )
        self.register_delete_key_handler(
            lambda key_id: self.logger.debug(
                "%s Delete key: %s (Server ID: %d)",
                self._log_prefix(),
                self.server_key_id_to_name.get(key_id),
                key_id,
            )
        )
        self.register_subscription_status_handler(
            self._default_subscription_status_handler
        )
        self.register_delete_record_handler(
            lambda key_id, topic_id: self.logger.debug(
                "%s Delete record: %s - %s",
                self._log_prefix(),
                self.server_key_id_to_name.get(key_id),
                self.server_topic_id_to_name.get(topic_id),
            )
        )
        self.register_record_update_handler(
            lambda key_id, topic_id, value: self.logger.debug(
                "%s Record update: %s - %s = %s",
                self._log_prefix(),
                self.server_key_id_to_name.get(key_id),
                self.server_topic_id_to_name.get(topic_id),
                value,
            )
        )

    def _default_subscription_status_handler(self, name: str, status: str) -> None:
        """Default handler for subscription status messages."""
        self.logger.info(
            "%s Subscription %s status: %s", self._log_prefix(), name, status
        )
        if status == "NeedsContinue":
            self.logger.info(
                "%s Snapshot size limit reached, sending SubscribeContinue for %s",
                self._log_prefix(),
                name,
            )
            self.send_subscribe_continue(name)

    def start(self) -> None:
        """Start the client and send introduction message."""
        self.running = True
        intro_msg = {
            "message_type": "Introduction",
            "value": {
                "version": self.version,
                "pid": self.pid,
                "heartbeat_timeout_interval": int(
                    self.scaled_heartbeat_timeout_interval * 1000
                ),
                "user": self.user,
                "application": self.application,
                "working_namespace": self.working_namespace,
            },
        }
        self.logger.debug("%s Queuing introduction message", self._log_prefix())
        self.send_message(intro_msg)
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self.heartbeat_thread.start()
        # Run the WebSocket connection in the asyncio event loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        self.logger.info("%s GAR processing loop completed", self._log_prefix())
        self.loop.close()
        self.stop()
        if self.stopped_callback:
            self.stopped_callback()

    def stop(self) -> None:
        """
        Stop the client and terminate all client operations.
        Note this does not block until the connection is closed.
        Register a stopped callback to be notified when the control loop has stopped.
        """
        if self.running:
            self.logger.info("%s Stopping GAR client", self._log_prefix())

        self.running = False

    def halt(self) -> None:
        """
        Stops the client without sending any pending messages.
        """
        self.stop()
        self.connected = False

    def logoff(self) -> None:
        """Send a logoff message to the server and stop the client."""
        msg = {"message_type": "Logoff"}
        self.send_message(msg)
        self.logger.debug("%s Sending logoff", self._log_prefix())
        self.stop()

    def __del__(self) -> None:
        """Clean up resources when the object is destroyed."""
        if self.loop and not self.loop.is_closed():
            self.loop.close()

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a JSON message through the WebSocket."""
        if self.running:
            asyncio.run_coroutine_threadsafe(self.message_queue.put(message), self.loop)
        else:
            self.logger.debug(
                "%s Client is not running; message not sent %s",
                self._log_prefix(),
                message,
            )

    def _heartbeat_loop(self) -> None:
        """Send periodic heartbeat messages."""
        while self.running:
            msg = {
                "message_type": "Heartbeat",
                "value": {
                    "u_milliseconds": int(time.time() * 1000),
                },
            }
            self.logger.debug("%s Sending heartbeat", self._log_prefix())
            self.send_message(msg)
            time.sleep(
                min(
                    10,
                    self.scaled_heartbeat_timeout_interval / 2,
                )
            )

    def check_heartbeat(self) -> None:
        """Check if the heartbeat has timed out."""
        # Enforce heartbeat timeout, with 10× grace for the very first beat
        if self._initial_grace_period:
            cutoff = self._initial_grace_deadline
        else:
            cutoff = self.last_heartbeat_time + self.scaled_heartbeat_timeout_interval
        if time.time() > cutoff:
            self.logger.warning(
                "%s Heartbeat failure; previous heartbeat: %.3fs ago, connected: %s",
                self._log_prefix(),
                time.time() - self.last_heartbeat_time,
                self.connected,
            )
            self.exit_code = 1
            self.halt()
            if self.heartbeat_timeout_callback:
                self.heartbeat_timeout_callback()

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming messages by calling registered handlers."""
        # self.logger.debug("Received: %s", message)

        subscription_group = 0
        msg_type = message.get("message_type")
        if msg_type == "TopicIntroduction":
            self.server_topic_id_to_name[message["value"]["topic_id"]] = message[
                "value"
            ]["name"]
            self.server_topic_name_to_id[message["value"]["name"]] = message["value"][
                "topic_id"
            ]
        elif msg_type == "KeyIntroduction":
            subscription_group = self.active_subscription_group
            self.server_key_id_to_name[message["value"]["key_id"]] = message["value"][
                "name"
            ]
            self.server_key_name_to_id[message["value"]["name"]] = message["value"][
                "key_id"
            ]
        elif msg_type == "DeleteKey":
            subscription_group = self.active_subscription_group
            # 1) drop deleted key from server map
            key_id = message["value"]["key_id"]
            self.server_key_name_to_id.pop(
                self.server_key_id_to_name.get(key_id) or "", None
            )
            self.server_key_id_to_name.pop(key_id, None)
        elif msg_type == "Heartbeat":
            # update last‐beat and clear initial grace on the very first one
            self.last_heartbeat_time = time.time()
            if self._initial_grace_period:
                # Signal first heartbeat detected
                self.logger.info(
                    "%s First heartbeat received from server",
                    self._log_prefix(),
                )
                self.first_heartbeat_received.set()
                self._initial_grace_period = False
        elif msg_type == "Introduction":
            value = message["value"]
            # 5) Clear out old server state on reconnect
            self.server_topic_id_to_name.clear()
            self.server_topic_name_to_id.clear()
            self.server_key_id_to_name.clear()
            self.server_key_name_to_id.clear()
            self.record_map.clear()
            # reset heartbeat timeout (in seconds)
            new_interval = value["heartbeat_timeout_interval"] / 1000.0
            if self.timeout_scale != 1.0:
                new_interval *= self.timeout_scale

            self.scaled_heartbeat_timeout_interval = max(
                self.scaled_heartbeat_timeout_interval,
                new_interval,
            )
            self.last_heartbeat_time = time.time()
            # 4) enable 10× grace window for the *first* heartbeat
            self._initial_grace_period = True
            self._initial_grace_deadline = (
                self.last_heartbeat_time + self.scaled_heartbeat_timeout_interval * 10
            )
        elif msg_type == "JSONRecordUpdate":
            subscription_group = self.active_subscription_group
            record_id = message["value"]["record_id"]
            key_id = record_id["key_id"]
            topic_id = record_id["topic_id"]
            record_value = message["value"]["value"]
            self.record_map[(key_id, topic_id)] = record_value
        elif msg_type == "SubscriptionStatus":
            # Route status notifications to the currently active subscription group
            subscription_group = self.active_subscription_group
        elif msg_type == "DeleteRecord":
            subscription_group = self.active_subscription_group
            value = message["value"]
            key_id = value["key_id"]
            topic_id = value["topic_id"]
            self.record_map.pop((key_id, topic_id), None)
        elif msg_type == "BatchUpdate":
            subscription_group = self.active_subscription_group
            value = message["value"]
            default_class = value.get("default_class")

            # Check if there's a specific batch update handler
            batch_handler_key = (
                f"BatchUpdate {subscription_group}"
                if subscription_group
                else "BatchUpdate"
            )
            has_batch_handler = batch_handler_key in self.message_handlers

            # Pre-check for individual handlers if no batch handler
            key_handler = None
            record_handler = None
            if not has_batch_handler:
                key_handler_key = (
                    f"KeyIntroduction {subscription_group}"
                    if subscription_group
                    else "KeyIntroduction"
                )
                key_handler = self.message_handlers.get(key_handler_key)

                record_handler_key = (
                    f"JSONRecordUpdate {subscription_group}"
                    if subscription_group
                    else "JSONRecordUpdate"
                )
                record_handler = self.message_handlers.get(record_handler_key)

            for key_update in value.get("keys", []):
                key_id = key_update["key_id"]
                key_name = key_update.get("name")

                # Handle key introduction if name is provided and key is new
                if key_name and key_id not in self.server_key_id_to_name:
                    self.server_key_id_to_name[key_id] = key_name
                    self.server_key_name_to_id[key_name] = key_id

                    # If no batch handler but key handler exists, call KeyIntroduction handler
                    if not has_batch_handler and key_handler:
                        # Determine class_list: use key's classes, or default_class, or None
                        key_classes = key_update.get("classes")
                        if not key_classes and key_update.get("class"):
                            key_classes = [key_update["class"]]
                        elif not key_classes and default_class:
                            key_classes = [default_class]

                        key_intro_msg = {
                            "message_type": "KeyIntroduction",
                            "value": {
                                "key_id": key_id,
                                "name": key_name,
                                **({"class_list": key_classes} if key_classes else {}),
                            },
                        }
                        key_handler(key_intro_msg)

                # Process topics for this key - topic IDs are now object keys
                topics_dict = key_update.get("topics", {})
                for topic_id_str, record_value in topics_dict.items():
                    topic_id = int(topic_id_str)
                    self.record_map[(key_id, topic_id)] = record_value

                    # If no batch handler but record handler exists, call JSONRecordUpdate handler
                    if not has_batch_handler and record_handler:
                        record_update_msg = {
                            "message_type": "JSONRecordUpdate",
                            "value": {
                                "record_id": {"key_id": key_id, "topic_id": topic_id},
                                "value": record_value,
                            },
                        }
                        record_handler(record_update_msg)

            # If there is a batch handler, call it
            if has_batch_handler:
                batch_handler = self.message_handlers[batch_handler_key]
                batch_handler(message)
        elif msg_type == "ActiveSubscription":
            self.active_subscription_group = message["value"]["subscription_group"]
        elif msg_type == "Logoff":
            self.logger.info("%s Received Logoff from server", self._log_prefix())
            self.running = False
        elif msg_type == "Error":
            self.logger.error(
                "%s GAR error: %s", self._log_prefix(), message["value"]["message"]
            )
            self.exit_code = 1
            self.stop()

        self.check_heartbeat()

        handler = self.message_handlers.get(
            f"{msg_type} {subscription_group}" if subscription_group else str(msg_type)
        )
        if handler:
            try:
                handler(message)
            except Exception as e:
                self.logger.exception(
                    "%s Error in handler while processing message %s: %s",
                    self._log_prefix(),
                    str(message),
                    str(e),
                )
                raise

    def subscribe_formatted(self, subscription_message_value: Dict[str, Any]):
        """Send an already-formatted subscription message
        Args:
            subscription_message_value: json representation of the gar `subscribe` struct
        """

        sub_msg = {
            "message_type": "Subscribe",
            "value": subscription_message_value,
        }
        self.logger.debug("Sending: %s", sub_msg)
        self.send_message(sub_msg)

    # pylint: disable=too-many-arguments
    def subscribe(
        self,
        name: str,
        subscription_mode: str = "Streaming",
        key_name: Optional[Union[str, list[str]]] = None,
        topic_name: Optional[Union[str, list[str]]] = None,
        class_name: Optional[Union[str, list[str]]] = None,
        key_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        exclude_key_filter: Optional[str] = None,
        exclude_topic_filter: Optional[str] = None,
        max_history: Optional[str] = None,
        include_derived: bool = False,
        trim_default_values: bool = False,
        working_namespace: Optional[str] = None,
        restrict_namespace: Optional[str] = None,
        density: Optional[str] = None,
        subscription_group: int = 0,
        subscription_set: Optional[str] = None,
        snapshot_size_limit: int = 0,
        nagle_interval: int = 0,
        limit: int = 0,
    ) -> None:
        """Send a subscription request using local IDs.

        Args:
            name: Must be unique among live subscriptions from the client
            subscription_mode: The subscription mode (e.g., "Streaming", "Snapshot")
            key_name: Filter to only these keys if nonempty
            topic_name: Filter to only these topics if nonempty
            class_name: Filter to only topics within these classes if nonempty
            key_filter: Include keys matching this regex (cannot use with key_name)
            topic_filter: Include topics matching this regex (cannot use with topic_name)
            exclude_key_filter: Exclude keys matching this regex (cannot use with key_name)
            exclude_topic_filter: Exclude topics matching this regex (cannot use with topic_name)
            max_history: Maximum history to include (history_type)
            include_derived: Include derived topics
            trim_default_values: Trim records containing default values from the snapshot
            working_namespace: Namespace for matching relative paths using topic filters
            restrict_namespace: Restricts topics and keys to children of restrict_namespace. Defaults to the working namespace. Use "::" for root / no restriction.
            density: For performance tuning
            subscription_group: For receiving notice of which subscription is receiving updates
            subscription_set: The subscription set identifier
            snapshot_size_limit: If > 0, snapshots will be broken up at this limit
            nagle_interval: Nagle interval in milliseconds
            limit: Limits the number of records returned in initial snapshot (0 = all)

        Raises:
            ValueError: If mutually exclusive parameters are used together
        """

        # Validate mutually exclusive parameters
        if key_name and (key_filter or exclude_key_filter):
            raise ValueError(
                "key_name cannot be used with key_filter or exclude_key_filter"
            )

        if topic_name and (topic_filter or exclude_topic_filter):
            raise ValueError(
                "topic_name cannot be used with topic_filter or exclude_topic_filter"
            )

        # Validate limit parameter usage
        if limit > 0 and subscription_mode == "Streaming":
            raise ValueError("limit cannot be used with streaming subscriptions")

        class_list: list[str] | None
        if isinstance(class_name, str):
            class_list = class_name.split()
        else:
            class_list = class_name

        single_class = (
            class_list[0]
            if isinstance(class_list, list) and len(class_list) == 1
            else None
        )

        if isinstance(key_name, str):
            key_names = key_name.split()
        elif key_name:
            key_names = key_name
        else:
            key_names = []

        key_id_list = [
            self.get_and_possibly_introduce_key_id(x, single_class) for x in key_names
        ]

        if isinstance(topic_name, str):
            topic_names = topic_name.split()
        elif topic_name:
            topic_names = topic_name
        else:
            topic_names = []

        topic_id_list = [
            self.get_and_possibly_introduce_topic_id(x) for x in topic_names
        ]

        # Build subscription message, filtering out None values
        value_dict: Dict[str, Any] = {
            "subscription_mode": subscription_mode,
            "name": name,
        }

        # Add optional fields only if they have values
        if subscription_set is not None:
            value_dict["subscription_set"] = subscription_set
        if max_history is not None:
            value_dict["max_history"] = max_history
        if snapshot_size_limit > 0:
            assert (
                snapshot_size_limit <= self.ws_buffer_size
            ), "Snapshot size limit cannot exceed ws_buffer_size"
            value_dict["snapshot_size_limit"] = snapshot_size_limit
        if nagle_interval > 0:
            value_dict["nagle_interval"] = nagle_interval
        if subscription_group > 0:
            value_dict["subscription_group"] = subscription_group
        if density is not None:
            value_dict["density"] = density
        if include_derived:
            value_dict["include_derived"] = include_derived
        if working_namespace:
            value_dict["working_namespace"] = working_namespace
        if restrict_namespace:
            value_dict["restrict_namespace"] = restrict_namespace
        if trim_default_values:
            value_dict["trim_default_values"] = trim_default_values
        if limit > 0:
            value_dict["limit"] = limit
        if key_id_list:
            value_dict["key_id_list"] = key_id_list
        if topic_id_list:
            value_dict["topic_id_list"] = topic_id_list
        if class_list:
            value_dict["class_list"] = class_list
        if key_filter:
            value_dict["key_filter"] = key_filter
        if exclude_key_filter:
            value_dict["exclude_key_filter"] = exclude_key_filter
        if topic_filter:
            value_dict["topic_filter"] = topic_filter
        if exclude_topic_filter:
            value_dict["exclude_topic_filter"] = exclude_topic_filter

        self.subscribe_formatted(value_dict)

    def send_subscribe_continue(self, name: str) -> None:
        """Send a SubscribeContinue message for a subscription name."""
        msg = {"message_type": "SubscribeContinue", "value": {"name": name}}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def get_and_possibly_introduce_key_id(
        self, name: str, class_name: Optional[Union[str, list[str]]] = None
    ) -> int:
        """Introduce a new key if not already known and return local key ID."""
        with self._key_lock:
            if name not in self.local_key_map:
                key_id = self.local_key_counter
                self.local_key_map[name] = key_id
                self.local_key_counter += 1
                if class_name:
                    if isinstance(class_name, str):
                        class_list = class_name.split()
                    else:
                        class_list = class_name
                    msg = {
                        "message_type": "KeyIntroduction",
                        "value": {
                            "key_id": key_id,
                            "name": name,
                            "class_list": class_list,
                        },
                    }
                else:
                    msg = {
                        "message_type": "KeyIntroduction",
                        "value": {"key_id": key_id, "name": name},
                    }
                # self.logger.debug("Sending: %s", msg)
                self.send_message(msg)
            return self.local_key_map[name]

    def get_and_possibly_introduce_topic_id(self, name: str) -> int:
        """Introduce a new topic if not already known and return local topic ID."""
        with self._topic_lock:
            if name not in self.local_topic_map:
                topic_id = self.local_topic_counter
                self.local_topic_map[name] = topic_id
                self.local_topic_counter += 1
                msg = {
                    "message_type": "TopicIntroduction",
                    "value": {"topic_id": topic_id, "name": name},
                }
                self.logger.debug("Sending: %s", msg)
                self.send_message(msg)
            return self.local_topic_map[name]

    def publish_delete_key(self, key_id: int) -> None:
        """Publish a DeleteKey message using a local key ID."""
        msg = {"message_type": "DeleteKey", "value": {"key_id": key_id}}
        # self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def delete_key(self, key: str) -> None:
        """Delete a key from the server if it exists in the local_key_map. Removes from the local key map, so safe to call multiple times with the same key."""
        key_id = self.local_key_map.get(key)
        if key_id:
            self.publish_delete_key(key_id)

    def publish_delete_record(self, key_id: int, topic_id: int) -> None:
        """Publish a DeleteRecord message using local key and topic IDs."""
        msg = {
            "message_type": "DeleteRecord",
            "value": {"key_id": key_id, "topic_id": topic_id},
        }
        # self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_unsubscribe(self, name: str) -> None:
        """Publish an Unsubscribe message for a subscription name."""
        msg = {"message_type": "Unsubscribe", "value": {"name": name}}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_shutdown(self) -> None:
        """Publish a Shutdown message."""
        msg = {"message_type": "Shutdown"}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_record_with_ids(self, key_id: int, topic_id: int, value: Any) -> None:
        """
        Publish a record update using explicit key and topic IDs.

        This method creates and sends a JSONRecordUpdate message to the GAR server
        using the provided key and topic IDs. Unlike publish_record(), this method
        does not perform any name-to-ID conversion or introduce new keys/topics.

        Args:
            key_id: The integer ID of the key for this record. This should be a valid
                   key ID that has already been introduced to the server.
            topic_id: The integer ID of the topic for this record. This should be a valid
                     topic ID that has already been introduced to the server.
            value: The value to publish for this record. Can be any JSON-serializable
                  data type (dict, list, string, number, boolean, or null).

        Returns:
            None
        """
        update_msg = {
            "message_type": "JSONRecordUpdate",
            "value": {
                "record_id": {"key_id": key_id, "topic_id": topic_id},
                "value": value,
            },
        }
        # self.logger.debug("Sending: %s", update_msg)
        self.send_message(update_msg)

    def publish_record(
        self,
        key_name: str,
        topic_name: str,
        value: Any,
        class_name: Optional[str] = None,
    ) -> None:
        """Publish a record update using names, converting to local IDs."""
        key_id = self.get_and_possibly_introduce_key_id(key_name, class_name)
        topic_id = self.get_and_possibly_introduce_topic_id(topic_name)
        self.publish_record_with_ids(key_id, topic_id, value)

    def route_query(
        self,
        key_list: Optional[list[str]] = None,
        topic_list: Optional[list[str]] = None,
        class_list: Optional[list[str]] = None,
        key_filter: Optional[str] = None,
        exclude_key_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        exclude_topic_filter: Optional[str] = None,
        history_types: Optional[list[str]] = None,
        working_namespace: Optional[str] = None,
        restrict_namespace: Optional[str] = None,
        exclude_namespace: Optional[str] = None,
        include_derived: bool = False,
        timeout: float = 10.0,
        subscription_group_server_keys: int = 0,
        subscription_group_server_records: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Query GAR deployment routing to find servers with matching publications.

        Uses the g::deployment schema to find servers that have publications
        intersecting with the specified record filter criteria.

        Args:
            key_list: List of key names to restrict to
            topic_list: List of topic names to restrict to
            class_list: List of class names to filter by
            key_filter: Key filter regex
            exclude_key_filter: Exclude key filter regex
            topic_filter: Topic filter regex
            exclude_topic_filter: Exclude topic filter regex
            history_types: List of history types to include
            working_namespace: Working namespace for topic filters
            restrict_namespace: Restrict to children of this namespace
            exclude_namespace: Exclude children of this namespace
            include_derived: Include derived topics
            timeout: Timeout in seconds for blocking mode
            subscription_group_server_keys: subscription group for server keys. If left at the
                default (0), a per-thread unique value will be chosen automatically.
            subscription_group_server_records: subscription group for server records. If left at the
                default (0), a per-thread unique value will be chosen automatically.

        Returns:
            Dict of server records.

        Raises:
            ConnectionError: If the client is not connected.
            TimeoutError: If the query timed out before completing.
        """
        # Ensure we are connected before attempting any operations
        if not self.connected:
            raise ConnectionError(
                f"{self._log_prefix()} GARClient.route_query called while not connected"
            )

        # Compute per-thread default subscription groups when using defaults
        if (
            subscription_group_server_keys == 0
            or subscription_group_server_records == 0
        ):
            tid = threading.get_ident()
            with self._route_query_counter_lock:
                if tid not in self._route_query_tid_counters:
                    self._route_query_tid_counter += 1
                    self._route_query_tid_counters[tid] = self._route_query_tid_counter
                counter = self._route_query_tid_counters[tid]

            if subscription_group_server_keys == 0:
                subscription_group_server_keys = 650704 + 2 * counter

            if subscription_group_server_records == 0:
                subscription_group_server_records = 650704 + 2 * counter + 1

        # Generate unique key for this query
        query_key = str(uuid.uuid4())

        # Build record_filter value
        record_filter = {
            "key_list": key_list or [],
            "topic_list": topic_list or [],
            "class_list": class_list or [],
            "working_namespace": working_namespace,
            "restrict_namespace": restrict_namespace,
            "exclude_namespace": exclude_namespace,
            "key_filter_regex": key_filter,
            "exclude_key_filter_regex": exclude_key_filter,
            "topic_filter_regex": topic_filter,
            "exclude_topic_filter_regex": exclude_topic_filter,
            "include_derived": include_derived,
            "history_types": history_types or [],
        }

        # Remove None values
        record_filter = {k: v for k, v in record_filter.items() if v is not None}

        result_container: Dict[str, Any] = {}
        result_ready = threading.Event()

        def cleanup():
            """Delete the temporary RecordFilter record"""
            self.delete_key(query_key)

        def handle_servers(servers_value: list[str]):
            """Handle servers list and fetch server records"""
            if not servers_value:
                result_container["servers"] = {}
                result_ready.set()
                cleanup()
                return

            # Subscribe to Server records for the returned server keys
            sub_name = f"route_query_servers_{query_key}"

            def process_server_records(key_id: int, topic_id: int, value: Any) -> None:
                """Collect server records"""
                key_name = self.server_key_id_to_name.get(key_id)
                topic_name = self.server_topic_id_to_name.get(topic_id)

                if key_name not in result_container["servers"]:
                    result_container["servers"][key_name] = {}
                result_container["servers"][key_name][topic_name] = value

            def on_server_status(_name: str, status: str) -> None:
                """Handle server subscription completion"""
                if status in ("Finished", "Streaming"):
                    result_container["result"] = result_container["servers"]
                    result_ready.set()
                    cleanup()

            # Set up handlers for server subscription
            self.register_record_update_handler(
                process_server_records, subscription_group_server_records
            )
            self.register_subscription_status_handler(
                on_server_status, subscription_group_server_records
            )

            # Subscribe to servers
            self.subscribe(
                name=sub_name,
                subscription_mode="Snapshot",
                key_name=servers_value,
                working_namespace="g::deployment::Server",
                class_name="g::deployment::Server",
                include_derived=True,
                subscription_group=subscription_group_server_records,
            )

        def process_record_filter(_key_id: int, _topic_id: int, value: Any) -> None:
            """Process RecordFilter records"""
            result_container["servers"] = {}
            handle_servers(value)

        def on_record_filter_status(_name: str, status: str) -> None:
            """Handle RecordFilter subscription status"""
            if status in ("Finished", "Streaming"):
                # If no servers topic received, we're done
                if "servers" not in result_container:
                    result_container["result"] = {}
                    result_ready.set()
                    cleanup()

        # Set up handlers
        self.register_record_update_handler(
            process_record_filter, subscription_group_server_keys
        )
        self.register_subscription_status_handler(
            on_record_filter_status, subscription_group_server_keys
        )

        # Publish the RecordFilter record
        self.publish_record(
            query_key,
            "g::deployment::RecordFilter::record_filter",
            record_filter,
            "g::deployment::RecordFilter",
        )

        # Subscribe to get the servers result
        sub_name = f"route_query_{query_key}"
        self.subscribe(
            name=sub_name,
            subscription_mode="Snapshot",
            key_name=query_key,
            working_namespace="g::deployment::RecordFilter",
            topic_name="g::deployment::RecordFilter::servers",
            class_name="g::deployment::RecordFilter",
            include_derived=True,
            subscription_group=subscription_group_server_keys,
        )

        # Blocking mode
        if result_ready.wait(timeout):
            return result_container.get("result")

        # Timeout: ensure cleanup then raise exception
        cleanup()
        raise TimeoutError(f"{self._log_prefix()} {sub_name} timed out")
