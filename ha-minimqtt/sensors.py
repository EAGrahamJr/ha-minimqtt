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

from datetime import timedelta
from enum import Enum

from base import AbstractBaseEntity, DeviceIdentifier, DeviceClass


class AbstractSensor(AbstractBaseEntity):
    def __init__(
        self,
        component: str,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        expires: timedelta = None,
        device_class: DeviceClass = None,
    ):
        super().__init__(component, unique_id, name, device)
        self._expires = expires
        self._class = device_class
        self._sensor_state = None

    @property
    def current_state(self):
        return self._sensor_state or ""

    @current_state.setter
    def current_state(self, value: str):
        """
        Set the current state of the sensor.

        Values should be translated to their "native" string representation (e.g. numbers shouldn't worry about
        rounding).
        :param value: the value to set/send
        :return: None
        """
        self._sensor_state = value
        self.send_current_state()

    @property
    def discovery(self):
        discovery_info = super().discovery
        discovery_info["entity_category"] = "diagnostic"
        discovery_info["device_class"] = self._class.value
        if self._expires > timedelta(seconds=1):
            discovery_info["expire_after"] = self._expires.total_seconds()
        return discovery_info


class BinaryDevice(DeviceClass):
    NONE = "none"
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


class BinarySensor(AbstractSensor):
    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        expires: timedelta = timedelta(0),
        device_class: BinaryDevice = BinaryDevice.NONE,
        off_delay: timedelta = timedelta(0),
    ):
        super().__init__(
            "binary_sensor", unique_id, name, device, expires, device_class
        )
        self._off_delay = off_delay
        self.icon = "mdi:door"
        self._sensor_state = "OFF"

    def discovery(self):
        disco = super().discovery
        self._class.add_discovery(disco)
        if self._off_delay > timedelta(seconds=1):
            disco["off_delay"] = int(self._off_delay.total_seconds())
        return disco

    @property
    def current_state(self):
        return self._sensor_state == "ON"

    @current_state.setter
    def current_state(self, value):
        self._sensor_state = "ON" if value else "OFF"
        self.send_current_state()


class StateClass(Enum):
    NONE = "none"
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


class AnalogDevice(DeviceClass):
    NONE = "none"
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


class AnalogSensor(AbstractSensor):

    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        expires: timedelta = None,
        device_class: AnalogDevice = AnalogDevice.NONE,
        state_class: StateClass = StateClass.NONE,
        unit_of_measurement: str = None,
        suggested_precision: int = None,
    ):
        super().__init__("sensor", unique_id, name, device, expires, device_class)

        self._state_class = state_class
        self._unit_of_measurement = unit_of_measurement
        self._suggested_precision = suggested_precision
        self.icon = "mdi:gauge"

    @property
    def discovery(self) -> dict:
        disco = super().discovery
        if self._suggested_precision is not None:
            disco["suggested_display_precision"] = self._suggested_precision
        self._class.add_discovery(disco, self._unit_of_measurement)
        return disco
