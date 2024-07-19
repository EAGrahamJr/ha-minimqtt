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
Basic "sensor" definitions -- either on/off or send a number.
"""
from ha_minimqtt._compatibility import ConstantList

from ha_minimqtt import BaseEntity, DeviceIdentifier, DeviceClass

# pylint: disable=R0801


class BinaryDevice(DeviceClass, ConstantList):
    """
    Defines the type of binary (on/off) sensors
    """

    BATTERY = "battery"
    BATTERY_CHARGING = "battery_charging"
    CARBON_MONOXIDE = "carbon_monoxide"
    COLD = "cold"
    CONNECTIVITY = "connectivity"
    DOOR = "door"
    GARAGE_DOOR = "garage_door"
    GAS = "gas"
    HEAT = "heat"
    LIGHT = "light"
    LOCK = "lock"
    MOISTURE = "moisture"
    MOTION = "motion"
    MOVING = "moving"
    OCCUPANCY = "occupancy"
    OPENING = "opening"
    PLUG = "plug"
    POWER = "power"
    PRESENCE = "presence"
    PROBLEM = "problem"
    RUNNING = "running"
    SAFETY = "safety"
    SMOKE = "smoke"
    SOUND = "sound"
    TAMPER = "tamper"
    UPDATE = "update"
    VIBRATION = "vibration"
    WINDOW = "window"


class BinarySensor(BaseEntity):
    """
    An on/off sensor.
    """

    # pylint: disable=R0913
    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        device_class: str = BinaryDevice.NONE,
        expires: int = None,
        off_delay: int = None,
    ):
        """
        Make one. the **component** is set to *binary_sensor*

        :param unique_id: a system-wide unique identifier
        :param name: friendly name
        :param device: what this thing is running on
        :param device_class: optional "type" of **BinaryDevice**
        :param expires: optional time **in seconds** when readings expire; default is "never" and
            minimum == 1
        :param off_delay: optional time to send an "off" command after sending "on"; default is
            "never" and minimum == 1
        """
        if device_class and device_class not in BinaryDevice.list():
            raise ValueError(f"'device_class {device_class} is not known")
        if off_delay and off_delay < 1:
            raise ValueError(f"'off_delay' {off_delay} must be >= 1 second")
        if expires and expires < 1:
            raise ValueError(f"'expires' {expires} must be >= 1")

        super().__init__(
            "binary_sensor",
            unique_id,
            name,
            device,
            device_class=BinaryDevice(device_class),
        )
        self._expires = expires
        self._off_delay = off_delay
        self.icon = "mdi:door"
        self._sensor_state = "OFF"

    def _add_other_discovery(self, disco: dict) -> dict:
        disco["entity_category"] = "diagnostic"
        if self._expires:
            disco["expire_after"] = self._expires

        if self._off_delay:
            disco["off_delay"] = int(self._off_delay)

        return disco

    def current_state(self):
        """
        :return: the current stored state of this sensor (**must** be set externally)
        """
        return self._sensor_state or ""

    def set_current_state(self, value):
        """
        Set the current state of the sensor. This is transmitted to HA.

        Must be one of "ON"/"OFF" (case-insensitive) or True/False
        :param value: the value to set/send
        """
        if isinstance(value, str):
            v = value.upper()
            if v not in ("ON", "OFF"):
                raise ValueError(f"'state' {value} must be ON or OFF")
            self._sensor_state = v
            self.send_current_state()

        elif isinstance(value, bool):
            self._sensor_state = "ON" if value else "OFF"
            self.send_current_state()
        else:
            raise ValueError(
                f"'state' {value} must be one of 'ON','OFF;, True, or False"
            )


# pylint: disable=R0903
class StateClass(ConstantList):
    """
    How analog data is accumulated/graphed. The default is MEASUREMENT.
    """

    NONE = "none"
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


class AnalogDevice(DeviceClass, ConstantList):
    """
    The various things HA knows about for numbers.
    """

    APPARENT_POWER = "apparent_power"
    AQI = "aqi"
    ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
    BATTERY = "battery"
    CARBON_MONOXIDE = "carbon_monoxide"
    CARBON_DIOXIDE = "carbon_dioxide"
    CURRENT = "current"
    DATA_RATE = "data_rate"
    DATA_SIZE = "data_rate"
    DATE = "date"
    DISTANCE = "distance"
    DURATION = "duration"
    ENERGY = "energy"
    ENERGY_STORAGE = "energy_storage"
    ENUM = "enum"
    FREQUENCY = "frequency"
    GAS = "gas"
    HUMIDITY = "humidity"
    ILLUMINANCE = "illuminance"
    IRRADIANCE = "irradiance"
    MOISTURE = "moisture"
    MONETARY = "monetary"
    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    NITROGEN_MONOXIDE = "nitrogen_monoxide"
    NITROUS_OXIDE = "nitrous_oxide"
    OZONE = "ozone"
    PH = "ph"
    PM1 = "pm1"
    PM10 = "pm10"
    PM25 = "pm25"
    POWER_FACTOR = "power_factor"
    POWER = "power"
    PRECIPITATION = "precipitation"
    PRECIPITATION_INTENSITY = "precipitation_intensity"
    PRESSURE = "pressure"
    REACTIVE_POWER = "reactive_power"
    SIGNAL_STRENGTH = "signal_strength"
    SOUND_PRESSURE = "sound_pressure"
    SPEED = "speed"
    SULPHUR_DIOXIDE = "sulphur_dioxide"
    TEMPERATURE = "temperature"
    TIMESTAMP = "timestamp"
    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"
    VOLATILE_ORGANIC_COMPOUNDS_PARTS = "volatile_organic_compounds_parts"
    VOLTAGE = "voltage"
    VOLUME = "volume"
    VOLUME_STORAGE = "volume_storage"
    WATER = "water"
    WEIGHT = "weight"
    WIND_SPEED = "wind_speed"


class AnalogSensor(BaseEntity):
    """
    Sends variable numeric data, typically on a regular basis or when "triggered" by a change.
    """

    # pylint: disable=R0913
    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        device_class: str = AnalogDevice.NONE,
        expires: int = None,
        state_class: str = None,
        unit_of_measurement: str = None,
        suggested_precision: int = None,
    ):
        """
        Make one. The **component** is set to "sensor".
        :param unique_id: a system-wide unique identifier
        :param name: friendly name
        :param device: what this thing is running on
        :param expires: optional time when readings expire; default is "never"
        :param device_class: optional "type" of sensor
        :param state_class: how the measurement is accumulated
        :param unit_of_measurement: what this represents; **note:** if using a *device_class*, this
            must match what HA expects for that class
        :param suggested_precision: how much info to work with; the default is to use the full
        value sent
        """
        if device_class and device_class not in AnalogDevice.list():
            raise ValueError(f"'device_class {device_class} is not known")
        if state_class and state_class not in StateClass.list():
            raise ValueError(f"'state_class {state_class} is not known")
        if expires and expires < 1:
            raise ValueError(f"'expires' {expires} must be >= 1")

        super().__init__(
            "sensor",
            unique_id,
            name,
            device,
            device_class=AnalogDevice(device_class, unit_of_measurement),
        )

        self._expires = expires
        self._state_class = state_class
        self._unit_of_measurement = unit_of_measurement
        self._suggested_precision = suggested_precision
        self._sensor_state = None
        self.icon = "mdi:gauge"

    def _add_other_discovery(self, disco: dict) -> dict:
        disco["entity_category"] = "diagnostic"
        if self._expires:
            disco["expire_after"] = self._expires

        if self._suggested_precision:
            disco["suggested_display_precision"] = self._suggested_precision

        return disco

    def current_state(self):
        """
        :return: the current stored state of this sensor (**must** be set externally)
        """
        return self._sensor_state or ""

    def set_current_state(self, value: float):
        """
        Set and send the current state of the sensor.
        :param value: **float** value (throws *ValueError* if not)
        """
        if not isinstance(value, float):
            raise ValueError(f"Expecting a float value: `{value}`")
        self._sensor_state = str(value)
        self.send_current_state()
