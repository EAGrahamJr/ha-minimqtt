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

#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
import json
import logging
from enum import Enum

try:
    from socket import gethostname
except ImportError:
    pass

try:
    from abc import ABC, abstractmethod
except ImportError:
    pass

from mqttwrapper import MQTTClientWrapper


class DeviceIdentifier:
    """
    Defines the particular "device" (typically the physical thing) doing HA stuff.

    This is typically the microcontroller or computer running the various entities.
    :param manufacturer: who has constructed the device (e.g. my Kotlin devices are "Kobot")
    :param model: which model of the manufacturer (e.g. "3B+" describes a "Raspberry Pi")
    :param identifier: the actual device identity - defaults to the network hostname
    """

    def __init__(self, manufacturer: str, model: str, identifier: str = gethostname()):
        if not manufacturer.strip():
            raise ValueError("'manufacturer' must not be blank.")
        if not model.strip():
            raise ValueError("'model' must not be blank.")
        if not identifier.strip():
            raise ValueError("'identifier' must not be blank.")
        self._manufacturer = manufacturer
        self._model = model
        self._identifier = identifier

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def model(self) -> str:
        return self._model

    @property
    def identifier(self) -> str:
        return self._identifier

    def as_json(self, unique_id: str) -> dict:
        """
        Create the discovery payload for this device.

        TODO don't know if the unique ID is actually doing anything here
        :param unique_id: also the unique identifier of the entity?
        :return: discovery payload
        """
        return {
            "identifiers": [unique_id, self.identifier],
            "name": self.identifier,
            "model": self.model,
            "manufacturer": self.manufacturer,
        }


# This is the default MQTT topic prefix -- you probably do not want to use it.
DEFAULT_MQTT_PREFIX = "kobots_ha/mqtt"


class AbstractBaseEntity(ABC):
    """
    The root of all the evil that exists here.

    :param component: identifies the HA specific "type" of entity
    :param unique_id: a system-wide unique identifier
    :param name: friendly name
    :param device: what this thing is running on
    """

    def __init__(
            self, component: str, unique_id: str, name: str, device: DeviceIdentifier
    ):
        if not component.strip():
            raise ValueError("'component' must not be blank.")
        if not unique_id.strip():
            raise ValueError("'uniqueId' must not be blank.")
        if not name.strip():
            raise ValueError("'name' must not be blank.")

        self._component = component
        self._unique_id = unique_id
        self._name = name
        self._device = device
        self._logger = logging.getLogger(type(self).__name__)
        self._connected = False
        self._deleted = False
        self._icon = "mdi:devices"
        self._topic_prefix = DEFAULT_MQTT_PREFIX
        self._client = None

    @property
    def component(self):
        return self._component

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device(self) -> DeviceIdentifier:
        return self._device

    @property
    def icon(self) -> str:
        """
        The icon used for this entity.

        :return: the icon name
        """
        return self._icon

    @icon.setter
    def icon(self, icon: str):
        """
        The icon used for this entity.

        :param icon: the icon to use
        """
        self._icon = icon

    @property
    def ha_connected(self) -> bool:
        return self._connected and not self._deleted

    @property
    def discovery(self) -> dict:
        """
        Create the auto-discovery payload for this entity.

        :return: the ready-to-publish discovery descriptor
        """
        return {
            "device": self._device.as_json(self._unique_id),
            "entity_category": "config",
            "icon": self._icon,
            "name": self._name,
            "schema": "json",
            "state_topic": self._topic_prefix,
            "unique_id": self._unique_id,
        }

    @property
    @abstractmethod
    def current_state(self) -> str:
        raise NotImplementedError

    @property
    def topic_prefix(self) -> str:
        return self._topic_prefix

    @topic_prefix.setter
    def topic_prefix(self, topic: str):
        self._topic_prefix = topic

    @property
    def status_topic(self):
        return f"{self.topic_prefix}/{self.unique_id}/state"

    def start(self, wrapper: MQTTClientWrapper):
        """
        "Starts" the entity.

        1) adds listeners to the MQTT client
        2) subscribes to the general HA status topic

        Note that the auto-discovery payload is sent on (re-)connect to the MQTT broker.

        :param wrapper: the "decorator" for whatever MQTT client is being used
        :return:
        """

        def on_connect(reconnect: bool):
            self.redo_connection()

        def on_disconnect():
            self._connected = False

        def on_homeassistant_status(message: str):
            if message == "online":
                self.redo_connection()
            else:
                self._connected = False

        wrapper.add_connect_listener(on_connect)
        wrapper.add_disconnect_listener(on_disconnect)
        wrapper.subscribe("homeassistant/status", on_homeassistant_status)
        self._client = wrapper

    def redo_connection(self):
        self._connected = True
        self.send_discovery()
        self._logger.info("Waiting 2 seconds for discovery to be processed")
        # TODO delay and send current state somehow?

    def send_discovery(self, discovery_payload: dict = None):
        """
        Send the auto-discovery payload if HA is available.

        :param discovery_payload: the payload to send or uses 'self.discovery' is not set
        :return: None
        """
        if self.ha_connected:
            payload = self.discovery if discovery_payload is None else discovery_payload
            jsons = json.dumps(payload)

            self._logger.info(f"Sending discovery for {self.unique_id}")
            self._client.publish(
                f"homeassistant/{self.component}/{self.unique_id}/config", jsons
            )

    def send_current_state(self, state: str = None):
        """
        Send the state if HA is available.

        :param state: state to send or uses 'self.current_state' if not set
        :return:
        """
        if self.ha_connected:
            pub_state = self.current_state if state is None else state
            self._client.publish(self.status_topic, pub_state)

    def remove(self):
        if self.ha_connected:
            self._logger.warning(f"Removing device {self.unique_id}")
            self._client.publish(
                f"homeassistant/{self.component}/{self.unique_id}/config", ""
            )
        self._deleted = True


class CommandEntity(AbstractBaseEntity):
    """
    An entity that takes input (e.g. commands) from HA.

    Implementations must over-ride the 'handle_command' method
    """

    def __init__(
            self, component: str, unique_id: str, name: str, device: DeviceIdentifier
    ):
        super().__init__(component, unique_id, name, device)

    @property
    def command_topic(self):
        return f"{self.topic_prefix}/{self.unique_id}/set"

    @abstractmethod
    def handle_command(self, payload: str):
        """
        Process this command.

        :param payload: a payload supposedly specific to this entity.
        :return: None
        """
        raise NotImplementedError

    def start(self, wrapper: MQTTClientWrapper):
        super().start(wrapper)
        self._client.subscribe(self.command_topic, self.handle_command)

    @property
    def discovery(self):
        disco = super().discovery
        disco["command_topic"] = self.command_topic
        return disco


class DeviceClass(Enum):
    """
    Extends an enum to update a discovery payload using this class and some measurement details.
    """

    def add_discovery(self, discovery_payload: dict, unit_of_measurement: str = None):
        if self.name != "NONE":
            discovery_payload.pop("icon", None)
            discovery_payload["device_class"] = self.value.lower()
        if unit_of_measurement is not None:
            discovery_payload["unit_of_measurement"] = unit_of_measurement
