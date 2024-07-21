#  MIT License
#
#  Copyright (c) 2024 E. A. (Ed) Graham, Jr.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""
An asyncio, Adafruit CircuitPython implementation of the MQTT client.

This is set up as a separate import so that other implementations may not necessarily be tied
to CircuitPython. It is **NOT** necessarily intended for high-speed reporting.
"""

import asyncio
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT

from ha_minimqtt._compatibility import logging
from ha_minimqtt import MQTTClientWrapper


# pylint: disable=R0902,W1201,W1203
class CircuitPythonWrapper(MQTTClientWrapper):
    """
    This client *also* manages the wifi connection, so it is not recommended for devices
    that have multiple uses for the radio. See HAMMFactory for an environment-based factory.
    """

    _mqtt_client = None

    # if the queue ever reaches this size, the device is sending too much data
    _publish_queue = []
    _subscribers = {}
    _connect_listeners = []
    _disconnect_listeners = []

    _logger = logging.getLogger("CircuitPythonMiniMqttWrapper")

    # pylint: disable=R0913
    def __init__(
        self,
        ssid: str,
        password: str,
        broker: str,
        port: int = 1883,
        loop_sleep: float = 1.0,
        loop_timeout: float = 1.0,
        reconnect_wait: float = 5.0,
        debug: bool = False,
    ):

        self._ssid = ssid
        self._password = password
        self._broker = broker
        self._port = port
        self._loop_sleep = loop_sleep
        self._loop_timeout = loop_timeout
        self._reconnect_wait = reconnect_wait

        self._connect_wifi_task = None

        if debug:
            self._logger.setLevel(logging.DEBUG)

    def add_connect_listener(self, callback) -> None:
        self._connect_listeners.append(callback)

    async def _notify_connect_listeners(self, reconnect: bool):
        """
        Execute all the "connect" call-backs
        :param reconnect: whether first time or not
        """
        for l in self._connect_listeners:
            l(reconnect)

    def add_disconnect_listener(self, callback) -> None:
        self._disconnect_listeners.append(callback)

    async def _notify_disconnect_listeners(self):
        """
        Execute all the "disconnect" call-backs
        """
        for l in self._disconnect_listeners:
            l()

    def subscribe(self, topic: str, callback) -> None:
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
            self._mqtt_client.subscribe(topic)

    def publish(self, topic: str, payload: str):
        self._logger.debug(f"Appending '{topic}: {payload}")
        self._publish_queue.append((topic, payload))

    async def _connect_wifi(self):
        """
        (Re-)Connect to the network
        """
        self._logger.debug("Connecting to WiFi")
        while not wifi.radio.connected:
            wifi.radio.connect(self._ssid, self._password)
            self._logger.info(
                f"Connected to WiFi - IP address: {wifi.radio.ipv4_address}"
            )

    async def _client_loop(self, client):
        """
        Execute the MQTT client loop (executes all the MQTT actions).

        :param client: the client
        """
        while True:
            try:

                # publish anything in the queue, FIFO
                pub_copy = self._publish_queue.copy()
                pub_copy.sort(reverse=True)
                self._publish_queue.clear()

                for topic, payload in pub_copy:
                    self._logger.debug(f"Pub to {topic} {payload}")
                    client.publish(topic, payload)

                # execulte the client loop (send, receive, heartbeat)
                client.loop(timeout=self._loop_timeout)
                await asyncio.sleep(self._loop_sleep)
            except (ValueError, RuntimeError) as e:
                self._logger.exception(e)
                await self._notify_disconnect_listeners()
                await self._connect_wifi()
                client.reconnect()
                await self._notify_connect_listeners(False)

    async def start(self):
        """
        Sets up the initial stuff and connects to the broker.

        :return: handle to the background task (never exits)
        """

        # connect to wifi, get the pool, and start the client loop
        await self._connect_wifi()

        pool = socketpool.SocketPool(wifi.radio)
        self._logger.debug(f"Create MQTT client {self._broker}:{self._port}")
        self._mqtt_client = MQTT.MQTT(
            broker=self._broker, port=self._port, socket_pool=pool
        )

        def message_received(_, topic, message):
            self._logger.debug(f"New message on topic {topic}: {message}")

            # "send" it to the appropriate call-backs"
            # note that this is called in a "blocking" manner because
            # entities don't "know" about asyncio
            subscribers = self._subscribers.get(topic)
            if subscribers:
                sub_list = subscribers.copy()
                for sub in sub_list:
                    sub(message)

        self._mqtt_client.on_message = message_received
        self._mqtt_client.connect()
        self._logger.info("MQTT connected")

        # don't care: this should run "forever"
        # pylint: disable=W0612
        ignored = asyncio.create_task(self._client_loop(self._mqtt_client))


# pylint: disable=C0415,R0903
class HAMMFactory:
    """
    Creates the above wrapper using the ENV and some defaults.
    """

    @staticmethod
    def create_wrapper():
        """
        Create a CirctuiPython wrapper for HA/mini-mqtt
        :return: the wrapper
        """
        import os

        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
        broker = os.getenv("HAMM_BROKER")
        port = int(os.getenv("HAMM_BROKER_PORT", "1883"))

        loop_sleep = float(os.getenv("HAMM_LOOP_SLEEP", "1"))
        loop_timeout = float(os.getenv("HAMM_LOOP_TIMEOUT", "1"))
        reconnect_delay = float(os.getenv("HAMM_RECONNECT_DELAY", "5"))

        return CircuitPythonWrapper(
            ssid, password, broker, port, loop_sleep, loop_timeout, reconnect_delay
        )
