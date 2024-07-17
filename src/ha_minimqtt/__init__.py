# MIT License
#
# Copyright (c) 2024 E. A. (Ed) Graham, Jr.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
The root of all evil that is this module. All entities derive from these "base" classes, which
provide the interactions with the underlying MQTT client wrapper.
"""
import json

from ha_minimqtt._compatibility import gethostname, ConstantList, logging
from ha_minimqtt.mqttwrapper import MQTTClientWrapper

# This is the default MQTT topic prefix -- you probably do not want to use it.
DEFAULT_MQTT_PREFIX = "kobots_ha/mqtt"


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
        """
        :return: the "manufacturer" of the device (e.g. "Kobots" is my "brand")
        """
        return self._manufacturer

    @property
    def model(self) -> str:
        """
        :return:the "model" of the device (e.g. "Servomatic!" has a lot of servos)
        """
        return self._model

    @property
    def identifier(self) -> str:
        """
        :return:the unique identifier for the device in the system
        """
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


class CommandHandler:
    """
    Anything that takes input (e.g. commands) from HA. When attached to a **BaseEntity**,
    it allows HA to send commands to the entity for execution.
    """

    def handle_command(self, payload: str):
        """
        Process this command.

        This should "block" until the execution finishes. Errors *should* be trapped, otherwise
        they will be relegated to the MQTT client wrapper.

        :param payload: a payload supposedly specific to this entity.
        :return: None
        """
        raise NotImplementedError

    @property
    def current_state(self) -> str:
        """
        **NOTE** this should be the "native" representation of whatever is being controlled. For
        example, if the thing is numerically controlled or a numeric sensor, the value should be
        **str(float)**, not a formatted string.
        :return: the current state of the thingie getting the command; by default, returns an
        empty string to signify "no state"
        """
        return ""


class DeviceClass:
    """
    An extension that is used for specific "types" as defined by HA.
    """

    NONE = "NONE"  # nobody home

    def __init__(self, device_class: str = NONE, unit_of_measurement: str = None):
        """
        Create a device class,
        :param device_class: optional name of the class; defaults to **NONE**
        :param unit_of_measurement: optional unit of measurement
        """
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement

    def add_to_discovery(self, disco: dict) -> dict:
        """
        Extends the payload with the class information if set. Also adds measurement details.
        :param disco: the dictionary to modify
        :return: the payload
        """
        if self._device_class:
            dc = self._device_class.lower()
            if dc != DeviceClass.NONE.lower():
                disco.pop("icon", None)
                disco["device_class"] = dc
        if self._unit_of_measurement:
            disco["unit_of_measurement"] = self._unit_of_measurement
        return disco


class BaseEntity:
    """
    The root of all the evil that exists here.
    """

    def __init__(
        self,
        component: str,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        command_handler: CommandHandler = None,
        device_class: DeviceClass = None,
    ):
        """
        Make the thing. All parameters are required.

        :param component: identifies the HA specific "type" of entity
        :param unique_id: a system-wide unique identifier
        :param name: friendly name
        :param device: what this thing is running on
        :param device_class: additional HA-specific typing of the entity (e.g. number types)
        :param command_handler: the *optional* handler to use if this entity accepts remote commands
        """

        if not component.strip():
            raise ValueError("'component' must not be blank.")
        if not unique_id.strip():
            raise ValueError("'uniqueId' must not be blank.")
        if not name.strip():
            raise ValueError("'name' must not be blank.")
        if device is None:
            raise ValueError("'device' is required")

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

        # Additional HA
        self._device_class = device_class
        # A lot of entities are "two-way"
        self._command_handler = command_handler

    @property
    def component(self):
        """
        :return: what type of entity this is
        """
        return self._component

    @property
    def name(self) -> str:
        """
        :return:the "friendly" (display) name
        """
        return self._name

    @property
    def unique_id(self) -> str:
        """
        :return:the unique identifier in the system
        """
        return self._unique_id

    @property
    def device(self) -> DeviceIdentifier:
        """
        :return: the thingie this is running on
        """
        return self._device

    @property
    def icon(self) -> str:
        """
        :return: the icon name (defaults to "mdi:devices")
        """
        return self._icon

    @icon.setter
    def icon(self, icon: str):
        """
        :param icon: the icon to use -- must be one of the "mdi:xxx" definitions supported by HA
        """
        self._icon = icon

    @property
    def ha_connected(self) -> bool:
        """
        :return: True if this entity thinks it's still talking to HA and has not been removed
        """
        return self._connected and not self._deleted

    def _add_other_discovery(self, disco: dict) -> dict:
        """
        Over-ride this to add more discovery information.

        :param disco: the current disco
        :return: the modified (maybe) disco
        """
        return disco

    @property
    def discovery(self) -> dict:
        """
        Create the auto-discovery payload for this entity. This is the default payload used by
        *send_discovery*

        :return: the ready-to-publish discovery descriptor
        """
        disco = {
            "device": self._device.as_json(self._unique_id),
            "entity_category": "config",
            "icon": self._icon,
            "name": self._name,
            "schema": "json",
            "state_topic": self._topic_prefix,
            "unique_id": self._unique_id,
        }
        if self._command_handler:
            disco["command_topic"] = self.command_topic
        if self._device_class:
            disco = self._device_class.add_to_discovery(disco)

        return self._add_other_discovery(disco)

    @property
    def current_state(self) -> str:
        """
        :return: the current state of the entity
        """
        if self._command_handler:
            return self._command_handler.current_state
        raise NotImplementedError

    @property
    def topic_prefix(self) -> str:
        """
        :return:the string prepended to the unique_id to create the status topic for MQTT; the
        default is DEFAULT_MQTT_TOPIC, which you don't want to use
        """
        return self._topic_prefix

    @topic_prefix.setter
    def topic_prefix(self, topic: str):
        """
        :param topic: set the string prepended to the unique_id to create the status topic for MQTT
        """
        self._topic_prefix = topic

    @property
    def status_topic(self):
        """
        :return: the MQTT topic this sends status on
        """
        return f"{self.topic_prefix}/{self.unique_id}/state"

    @property
    def command_topic(self):
        """
        :return: the command topic for the entity, if used for a **CommandHandler**
        """
        return f"{self.topic_prefix}/{self.unique_id}/set"

    def start(self, wrapper: MQTTClientWrapper):
        """
        "Starts" the entity.

        1) adds listeners to the MQTT client
        2) subscribes to the general HA status topic

        Note that the auto-discovery payload is sent on (re-)connect to the MQTT broker.

        :param wrapper: the "decorator" for whatever MQTT client is being used
        """

        def on_connect(reconnect: bool):
            self._logger.info("Connecting - reconnect %r", reconnect)
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

        ## if there's a handler, wire it in
        if self._command_handler:

            def handle_command(payload: str):
                # once the command is handled, trigger a status send automagically to avoid
                # circular dependencies
                self._command_handler.handle_command(payload)
                self.send_current_state()

            topic = f"{self.topic_prefix}/{self.unique_id}/set"
            wrapper.subscribe(topic, handle_command)

        self._client = wrapper

        # assume ready to go
        self.redo_connection()

    def redo_connection(self):
        """
        Reset the connetion and re-send discovery.
        """
        self._connected = True
        self.send_discovery()

    def send_discovery(self, discovery_payload: dict = None):
        """
        Send the auto-discovery payload, if connected to the broker. Does **not** throw an error
        if not.

        :param discovery_payload: the payload to send or uses 'self.discovery' is not set
        """
        if self.ha_connected:
            payload = self.discovery if discovery_payload is None else discovery_payload
            jsons = json.dumps(payload)

            self._logger.info("Sending discovery for '%s'", self.unique_id)
            self._client.publish(
                f"homeassistant/{self.component}/{self.unique_id}/config", jsons
            )

    def send_current_state(self, state: str = None):
        """
        Send the state, if connected to the broker. Does **not** throw an error if not.

        :param state: state to send or uses 'self.current_state' if not set
        """
        if self.ha_connected:
            pub_state = self.current_state if state is None else state
            self._client.publish(self.status_topic, pub_state)

    def remove(self):
        """
        Remove the entity from HA, if connected to the broker. Does **not** throw an error if not.
        Once all entities are removed, the device is also removed.
        """
        if self.ha_connected:
            self._logger.warning("Removing device %s", self.unique_id)
            self._client.publish(
                f"homeassistant/{self.component}/{self.unique_id}/config", ""
            )
        self._deleted = True


class NumberDisplayMode(ConstantList):
    """
    Defines how HA will display "numeric" entities.
    """

    AUTO = "auto"
    BOX = "box"
    SLIDER = "slider"