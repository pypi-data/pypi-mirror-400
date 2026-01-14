import asyncio
import websockets
import json
import logging
from typing import Optional, Any, Dict, List, Callable, Union
from enum import Enum
import inspect
from dataclasses import dataclass
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocketHelper")


class WSMessageType(Enum):
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"


@dataclass
class WSConnection:
    uri: str
    websocket: Any
    connected_at: float
    is_connected: bool = False


class WebSocketHelper:
    _connections: Dict[str, WSConnection] = {}
    _message_handlers: Dict[str, List[Callable]] = {}
    _connection_handlers: Dict[str, List[Callable]] = {}

    #######################
    # SERVER METHODS (FIXED)
    #######################
    @staticmethod
    async def start_server(
        host: str = "localhost",
        port: int = 8765,
        message_handler: Optional[Callable] = None,
    ):
        """Start WebSocket server and handle client connections"""

        async def handler(websocket, path):
            client_id = (
                f"client_{websocket.remote_address[0]}_{websocket.remote_address[1]}"
            )
            logger.info(f"[Server] New client connected: {client_id}")

            # Store the connection immediately when client connects
            WebSocketHelper._connections[client_id] = WSConnection(
                uri=f"ws://{host}:{port}",
                websocket=websocket,
                connected_at=time.time(),
                is_connected=True,
            )

            await WebSocketHelper._trigger_connection_handlers(client_id, "connected")

            try:
                async for message in websocket:
                    logger.info(f"[Server] Received from {client_id}: {message}")

                    # Try to parse as JSON
                    try:
                        parsed_message = json.loads(message)
                        message_type = WSMessageType.JSON

                        # Handle registration message
                        if (
                            isinstance(parsed_message, dict)
                            and parsed_message.get("action") == "register"
                        ):
                            new_client_id = parsed_message.get("client_id", client_id)
                            if new_client_id != client_id:
                                # Update client ID if different
                                WebSocketHelper._connections[new_client_id] = (
                                    WebSocketHelper._connections[client_id]
                                )
                                del WebSocketHelper._connections[client_id]
                                client_id = new_client_id
                                logger.info(
                                    f"[Server] Client registered as: {client_id}"
                                )

                            await websocket.send(
                                json.dumps(
                                    {
                                        "status": "registered",
                                        "client_id": client_id,
                                        "message": "Successfully registered with server",
                                    }
                                )
                            )
                            continue

                    except json.JSONDecodeError:
                        parsed_message = message
                        message_type = WSMessageType.TEXT

                    # Call custom message handler if provided
                    if message_handler:
                        response = await message_handler(
                            parsed_message, message_type, client_id
                        )
                        if response:
                            await websocket.send(
                                json.dumps(response)
                                if isinstance(response, dict)
                                else str(response)
                            )
                    else:
                        # Default echo behavior
                        echo_response = {
                            "echo": parsed_message,
                            "timestamp": time.time(),
                        }
                        await websocket.send(json.dumps(echo_response))

            except websockets.exceptions.ConnectionClosed:
                logger.info(f"[Server] Client disconnected: {client_id}")
            except Exception as e:
                logger.error(f"[Server] Error with client {client_id}: {e}")
            finally:
                # Clean up connection
                if client_id in WebSocketHelper._connections:
                    del WebSocketHelper._connections[client_id]
                await WebSocketHelper._trigger_connection_handlers(
                    client_id, "disconnected"
                )

        # Start the server
        server = await websockets.serve(handler, host, port)
        logger.info(f"[Server] WebSocket server started on ws://{host}:{port}")
        return server

    #######################
    # CLIENT METHODS
    #######################
    @staticmethod
    async def connect(uri: str, connection_id: str = "default") -> bool:
        """Connect to WebSocket server as client"""
        try:
            if (
                connection_id in WebSocketHelper._connections
                and WebSocketHelper._connections[connection_id].is_connected
            ):
                logger.info(f"[Client] Connection {connection_id} already exists")
                return True

            websocket = await websockets.connect(uri)
            WebSocketHelper._connections[connection_id] = WSConnection(
                uri=uri,
                websocket=websocket,
                connected_at=time.time(),
                is_connected=True,
            )

            logger.info(f"[Client] Connected to {uri} as {connection_id}")
            await WebSocketHelper._trigger_connection_handlers(
                connection_id, "connected"
            )

            # Start background message listener
            asyncio.create_task(WebSocketHelper._listen_for_messages(connection_id))

            return True

        except Exception as e:
            logger.error(f"[Client] Failed to connect to {uri}: {e}")
            await WebSocketHelper._trigger_connection_handlers(connection_id, "failed")
            return False

    @staticmethod
    async def _listen_for_messages(connection_id: str):
        """Listen for incoming messages on client connection"""
        try:
            connection = WebSocketHelper._connections[connection_id]
            async for message in connection.websocket:
                logger.info(f"[Client] {connection_id} received: {message}")

                # Trigger message handlers
                await WebSocketHelper._trigger_message_handlers(message, connection_id)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[Client] Connection closed: {connection_id}")
            if connection_id in WebSocketHelper._connections:
                WebSocketHelper._connections[connection_id].is_connected = False
                await WebSocketHelper._trigger_connection_handlers(
                    connection_id, "disconnected"
                )

    @staticmethod
    async def send_message(
        message: Union[str, dict],
        connection_id: str = "default",
        wait_response: bool = False,
        timeout: int = 10,
    ) -> Optional[Any]:
        """Send message to WebSocket connection"""
        if connection_id not in WebSocketHelper._connections:
            logger.error(f"[Send] Connection {connection_id} not found")
            return None

        connection = WebSocketHelper._connections[connection_id]
        if not connection.is_connected:
            logger.error(f"[Send] Connection {connection_id} is not connected")
            return None

        try:
            # Prepare message
            if isinstance(message, dict):
                message_to_send = json.dumps(message)
            else:
                message_to_send = str(message)

            logger.info(f"[Send] Sending to {connection_id}: {message_to_send}")
            await connection.websocket.send(message_to_send)

            if wait_response:
                response = await asyncio.wait_for(
                    connection.websocket.recv(), timeout=timeout
                )
                logger.info(f"[Send] Response from {connection_id}: {response}")
                return response

            return None

        except Exception as e:
            logger.error(f"[Send] Error sending to {connection_id}: {e}")
            return None

    #######################
    # UTILITY METHODS
    #######################
    @staticmethod
    async def _trigger_message_handlers(message: str, connection_id: str):
        """Trigger registered message handlers"""
        for handlers in WebSocketHelper._message_handlers.values():
            for handler in handlers:
                try:
                    await handler(message, connection_id)
                except Exception as e:
                    logger.error(f"[Handler] Error in message handler: {e}")

    @staticmethod
    async def _trigger_connection_handlers(connection_id: str, event_type: str):
        """Trigger connection event handlers"""
        if event_type in WebSocketHelper._connection_handlers:
            for handler in WebSocketHelper._connection_handlers[event_type]:
                try:
                    await handler(connection_id, event_type)
                except Exception as e:
                    logger.error(f"[Handler] Error in connection handler: {e}")

    @staticmethod
    def is_connected(connection_id: str = "default") -> bool:
        """Check if connection is active"""
        return (
            connection_id in WebSocketHelper._connections
            and WebSocketHelper._connections[connection_id].is_connected
        )

    @staticmethod
    def get_connected_clients() -> List[str]:
        """Get list of all connected client IDs"""
        return [
            conn_id
            for conn_id, conn in WebSocketHelper._connections.items()
                if conn.is_connected
        ]

    @staticmethod
    async def broadcast_message(message: Union[str, dict]):
        print("message", message)
        """Send message to all connected clients"""
        sent_count = 0
        for connection_id in WebSocketHelper.get_connected_clients():
            try:
                await WebSocketHelper.send_message(message, connection_id)
                sent_count += 1
            except Exception as e:
                logger.error(f"[Broadcast] Failed to send to {connection_id}: {e}")

        logger.info(f"[Broadcast] Sent to {sent_count} clients")
        return sent_count

    @staticmethod
    async def close_all_connections():
        """Close all active connections"""
        for connection_id in list(WebSocketHelper._connections.keys()):
            try:
                connection = WebSocketHelper._connections[connection_id]
                if connection.is_connected:
                    await connection.websocket.close()
                del WebSocketHelper._connections[connection_id]
            except Exception as e:
                logger.error(f"[Close] Error closing {connection_id}: {e}")

    # Event handler decorators
    @staticmethod
    def on_message(message_type: str = "default"):
        def decorator(func):
            if message_type not in WebSocketHelper._message_handlers:
                WebSocketHelper._message_handlers[message_type] = []
            WebSocketHelper._message_handlers[message_type].append(func)
            return func

        return decorator

    @staticmethod
    def on_connection(event_type: str):
        def decorator(func):
            if event_type not in WebSocketHelper._connection_handlers:
                WebSocketHelper._connection_handlers[event_type] = []
            WebSocketHelper._connection_handlers[event_type].append(func)
            return func

        return decorator
