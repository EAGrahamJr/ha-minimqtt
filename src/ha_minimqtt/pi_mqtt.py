import asyncio
import logging
from typing import Callable
import paho.mqtt.client as mqtt
from ha_minimqtt import MQTTClientWrapper


import socket as skt
from urllib.parse import urlparse


class LinuxSocketPool:
    AF_INET = skt.AF_INET
    SOCK_STREAM = skt.SOCK_STREAM

    def socket(self, family=skt.AF_INET, type=skt.SOCK_STREAM, proto=0):
        return skt.socket(family, type, proto)

    def getaddrinfo(
        self, host, port, family=skt.AF_INET, type=skt.SOCK_STREAM, proto=0, flags=0
    ):
        return skt.getaddrinfo(host, port, family, type, proto, flags)


def PiHAMMFactory():
    """
    Creates a CircuitPython wrapper for a Raspberry Pi using a simple `settings.properties` file
    in lieu of environment variables.
    """

    def _clean_value(raw: str) -> str:
        value = raw.strip()
        if len(value) >= 2 and ((value[0] == value[-1]) and value[0] in ('"', "'")):
            value = value[1:-1].strip()
        return value

    settings: dict[str, str] = {}
    with open("settings.properties", "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            settings[key.strip()] = _clean_value(value)

    broker_raw = settings.get("HAMM_BROKER", "")
    if not broker_raw:
        raise ValueError("HAMM_BROKER must be set in settings.properties")

    broker = broker_raw
    port = int(settings.get("HAMM_BROKER_PORT", "1883") or "1883")

    # Allow mqtt://host:port or tcp://host:port or bare host:port in HAMM_BROKER
    if "://" in broker_raw:
        parsed = urlparse(broker_raw)
        if parsed.hostname:
            broker = parsed.hostname
        if parsed.port:
            port = parsed.port
    elif ":" in broker_raw and broker_raw.count(":") == 1:
        host_part, port_part = broker_raw.split(":", 1)
        if host_part.strip():
            broker = host_part.strip()
        if port_part.strip():
            port = int(port_part.strip())

    client_id = settings.get("HAMM_CLIENT_ID") or None

    return PiPythonWrapper(
        broker=broker,
        port=port,
        client_id=client_id,
    )


class PiPythonWrapper(MQTTClientWrapper):
    """
    CircuitPython wrapper for HA/mini-mqtt use on a Raspberry Pi. Similar to the
    CircuitPythonWrapper, but uses the native socketpool from the OS.

    This requires the `paho-mqtt` library, which can be installed via `pip install paho-mqtt`.
    """

    __mqtt_client: mqtt.Client

    _subscribers = {}
    _connect_listeners = []
    _disconnect_listeners = []

    def __init__(
        self,
        broker: str,
        port: int = 1883,
        client_id: str | None = None,
    ):
        """
        Initialize the wrapper
        :param broker: MQTT broker address
        :param port: MQTT broker port
        :param client_id: MQTT client ID
        """
        self._broker = broker
        self._port = port

        self._client_id = client_id
        self._logger = logging.getLogger("PiPythonWrapper")

    @property
    def client_id(self):
        """
        :return: the set client ID (or *None* if not set)
        """
        return self._client_id

    def add_connect_listener(self, callback: Callable[[bool], None]) -> None:
        self._connect_listeners.append(callback)

    def _notify_connect_listeners(
        self, client, userdata, flags, reason_code, properties
    ):
        """
        Execute all the "connect" call-backs
        :param reconnect: whether first time or not
        """
        reconnect = self.__mqtt_client is not None and self.__mqtt_client.is_connected()
        for listener in self._connect_listeners:
            listener(reconnect)

        # after connect, re-subscribe to all topics
        for topic in self._subscribers.keys():
            self._logger.info(f"Re-subscribing to '{topic}'")
            self.__mqtt_client.subscribe(topic)

    def add_disconnect_listener(self, callback: Callable[[None], None]) -> None:
        self._disconnect_listeners.append(callback)

    def _notify_disconnect_listeners(
        self, client, userdata, flags, reason_code, properties
    ):
        """
        Execute all the "disconnect" call-backs
        """
        for listener in self._disconnect_listeners:
            listener()

    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        already_subbed = self._subscribers.get(topic)
        self._logger.debug(
            f"Adding sub to {topic} of {len(already_subbed) if already_subbed else 0}"
        )
        needs_sub = False
        if not already_subbed:
            already_subbed = []
            needs_sub = True
        already_subbed.append(callback)
        self._subscribers[topic] = already_subbed

        # if this is a new subscription, add it to the client
        if needs_sub:
            self._logger.info(f"Subscribing to '{topic}'")
            self.__mqtt_client.subscribe(topic)

    def publish(self, topic: str, payload: str, retain: bool = False, qos: int = 0):
        self._logger.debug(f"Publishing '{topic}': {payload}")
        self.__mqtt_client.publish(topic=topic, payload=payload, qos=qos, retain=retain)

    async def alive_check(self) -> None:
        """
        Periodic alive check
        """
        while True:
            await asyncio.sleep(30)
            self.__mqtt_client.publish("kobots/alive", self._client_id)

    async def start(self):
        """
        Sets up the initial stuff and connects to the broker.

        :return: handle to the background task (never exits)
        """
        self._logger.info(f"Create MQTT client {self._broker}:{self._port}")

        client_kwargs = {}
        if self._client_id is not None:
            client_kwargs["client_id"] = self._client_id

        self.__mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore

        def message_received(client, userdata, msg):
            topic = getattr(msg, "topic", "")
            payload = getattr(msg, "payload", b"")

            if isinstance(payload, (bytes, bytearray)):
                message = payload.decode(errors="replace")
            else:
                message = str(payload)

            self._logger.debug(f"New message on topic {topic}: {message}")

            # "send" it to the appropriate call-backs"
            # note that this is called in a "blocking" manner because
            # entities don't "know" about asyncio
            subscribers = self._subscribers.get(topic)
            if subscribers:
                sub_list = subscribers.copy()
                for sub in sub_list:
                    sub(message)

        self.__mqtt_client.on_message = message_received
        self.__mqtt_client.on_connect = self._notify_connect_listeners
        self.__mqtt_client.on_disconnect = self._notify_disconnect_listeners
        self._logger.info("Starting connectinon")
        self.__mqtt_client.connect(self._broker, self._port)
        self._logger.info("MQTT connected")

        self.__mqtt_client.loop_start()
        asyncio.create_task(self.alive_check())
