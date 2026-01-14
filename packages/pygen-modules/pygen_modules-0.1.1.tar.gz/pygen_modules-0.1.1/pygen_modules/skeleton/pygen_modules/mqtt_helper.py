"""| Code | Meaning                                         |
| ---- | ----------------------------------------------- |
| 0    | Connection successful [OK]                         |
| 1    | Connection refused – incorrect protocol version |
| 2    | Connection refused – invalid client identifier  |
| 3    | Connection refused – server unavailable         |
| 4    | Connection refused – bad username or password   |
| 5    | Connection refused – not authorized ❌           |
"""

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
from typing import Optional, Callable
import time


class MqttHelper:
    client: Optional[mqtt.Client] = None
    _custom_on_message: Optional[Callable] = None
    _is_connected = False
    _subscribed_topics = set()

    @classmethod
    def on_connect(cls, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected successfully (rc={rc})")
            cls._is_connected = True

            for topic in cls._subscribed_topics:
                client.subscribe(topic)
                print(f"[MQTT] Re-subscribed to: {topic}")
        else:
            print(f"[MQTT] Connection failed with code: {rc}")
            cls._is_connected = False

    @classmethod
    def on_disconnect(cls, client, userdata, rc):
        print(f"[MQTT] Disconnected with code: {rc}")
        cls._is_connected = False

    @classmethod
    def default_message_handler(cls, client, userdata, msg):
        """Default built-in message handler"""
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)

            endpoint = data.get("endpoint", "unknown")
            message_type = data.get("type", "unknown")

            print("\n" + "=" * 60)
            print(f"[MQTT RECEIVED]")
            print(f"  Topic: {msg.topic}")
            print(f"  Type: {message_type}")
            print(f"  Endpoint: {endpoint}")
            print(f"  Data: {data.get('data')}")
            print("=" * 60 + "\n")

        except json.JSONDecodeError as e:
            print(f"[MQTT ERROR] Invalid JSON: {e}")
            print(f"[MQTT RAW] {msg.payload.decode()}")
        except Exception as e:
            print(f"[MQTT ERROR] Could not process message: {e}")

    @classmethod
    def on_message(cls, client, userdata, msg):
        """Message handler that uses custom or default handler"""
        # Use custom handler if set, otherwise use default
        if cls._custom_on_message:
            cls._custom_on_message(client, userdata, msg)
        else:
            cls.default_message_handler(client, userdata, msg)

    @classmethod
    def on_subscribe(cls, client, userdata, mid, granted_qos):
        print(f"[MQTT] Subscription confirmed (mid={mid}, qos={granted_qos})")

    # @classmethod
    # def connect(cls, broker: str, port: int = 1883, client_id: str = "FastAPI_Client"):
    #     """Connect to MQTT broker"""
    #     if cls.client and cls._is_connected:
    #         print("[MQTT] Already connected, skipping reconnection")
    #         return

    #     try:
    #         cls.client = mqtt.Client(
    #             client_id=client_id,
    #             callback_api_version=CallbackAPIVersion.VERSION1
    #         )
    #         cls.client.on_connect = cls.on_connect
    #         cls.client.on_disconnect = cls.on_disconnect
    #         cls.client.on_message = cls.on_message
    #         cls.client.on_subscribe = cls.on_subscribe

    #         print(f"[MQTT] Connecting to {broker}:{port}...")
    #         cls.client.connect(broker, port, 60)
    #         cls.client.loop_start()

    #         timeout = 5
    #         start_time = time.time()
    #         while not cls._is_connected and (time.time() - start_time) < timeout:
    #             time.sleep(0.1)

    #         if cls._is_connected:
    #             print("[MQTT] Connection established successfully")
    #         else:
    #             print("[MQTT] Connection timeout")

    #     except Exception as e:
    #         print(f"[MQTT] Connection error: {e}")
    #         cls._is_connected = False
    @classmethod
    def connect(cls, broker: str, port: int = 443, client_id: str = "FastAPI_Client"):
        """Connect to MQTT broker over secure WebSocket"""
        if cls.client and cls._is_connected:
            print("[MQTT] Already connected, skipping reconnection")
            return

        try:
            cls.client = mqtt.Client(
                client_id=client_id,
                transport="websockets",
                callback_api_version=CallbackAPIVersion.VERSION1,
            )

            # Set authentication
            cls.client.username_pw_set("mqtt_user", "dbvnp6tNoQW0Gjzr")

            # Enable SSL for secure connection (wss)
            cls.client.tls_set()

            # Assign event callbacks
            cls.client.on_connect = cls.on_connect
            cls.client.on_disconnect = cls.on_disconnect
            cls.client.on_message = cls.on_message
            cls.client.on_subscribe = cls.on_subscribe

            print(f"[MQTT] Connecting to {broker}:{port} via WSS...")

            cls.client.ws_set_options(path="/mqtt")
            cls.client.connect(broker, port, 60)
            cls.client.loop_start()

            timeout = 5
            start_time = time.time()
            while not cls._is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if cls._is_connected:
                print("[MQTT] Connection established successfully")
            else:
                print("[MQTT] Connection timeout")

        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            cls._is_connected = False

    @classmethod
    def subscribe(cls, topic: str):
        """Subscribe to a topic"""
        if not cls.client:
            print("[MQTT] Client not initialized!")
            return False

        if not cls._is_connected:
            print("[MQTT] Client not connected!")
            return False

        try:
            result = cls.client.subscribe(topic)
            cls._subscribed_topics.add(topic)
            print(f"[MQTT] Subscribed to: {topic}")
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"[MQTT] Subscription error: {e}")
            return False

    @classmethod
    def publish(cls, topic: str, message: str):
        """Publish a message to a topic"""
        if not cls.client:
            print("[MQTT] Client not initialized!")
            return False

        if not cls._is_connected:
            print("[MQTT] Client not connected, cannot publish!")
            return False

        try:
            result = cls.client.publish(topic, message, qos=1)
            result.wait_for_publish(timeout=2)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT PUBLISHED] {topic} -> {message}")
                return True
            else:
                print(f"[MQTT PUBLISH FAILED] rc={result.rc}")
                return False
        except Exception as e:
            print(f"[MQTT] Publish error: {e}")
            return False

    @classmethod
    def set_on_message(cls, callback: Optional[Callable]):
        """
        Set custom message handler. Pass None to use default handler.
        """
        cls._custom_on_message = callback
        if callback:
            print("[MQTT] Custom message handler registered")
        else:
            print("[MQTT] Using default message handler")

    @classmethod
    def is_connected(cls) -> bool:
        """Check if connected to MQTT broker"""
        return cls._is_connected

    @classmethod
    def disconnect(cls):
        """Disconnect from MQTT broker"""
        if cls.client:
            cls._is_connected = False
            cls.client.loop_stop()
            cls.client.disconnect()
            print("[MQTT] Disconnected")
