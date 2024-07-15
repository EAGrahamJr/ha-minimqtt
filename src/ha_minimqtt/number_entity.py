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
Numeric entity: reports and responds to "number" commands.
"""

from enum import Enum

from base import CommandEntity, DeviceIdentifier, DeviceClass

from _compatibility import ABC, abstractmethod


# pylint: disable=R0801,C0103,R0903
class NumericDevice(DeviceClass):
    """
    The various things HA knows about for numbers. See `Device class
    <https://www.home-assistant.io/integrations/number/#device-class>`_
    """

    NONE = "none"
    APPARENT_POWER = "apparent_power"
    AQI = "aqi"
    ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
    BATTERY = "battery"
    CARBON_MONOXIDE = "carbon_monoxide"
    CARBON_DIOXIDE = "carbon_dioxide"
    CURRENT = "current"
    DATA_RATE = "data_rate"
    DATA_SIZE = "data_size"
    DISTANCE = "distance"
    DURATION = "duration"
    ENERGY = "energy"
    ENERGY_STORAGE = "energy_storage"
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
    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"
    VOLATILE_ORGANIC_COMPOUNDS_PARTS = "volatile_organic_compounds_parts"
    VOLTAGE = "voltage"
    VOLUME = "volume"
    VOLUME_STORAGE = "volume_storage"
    WATER = "water"
    WEIGHT = "weight"
    WIND_SPEED = "wind_speed"


class DisplayMode(Enum):
    """
    Defines how HA will display the entity.
    """

    AUTO = "auto"
    BOX = "box"
    SLIDER = "slider"


class NumberHandler(ABC):
    """
    Handle the input from a number entity.
    """

    @property
    @abstractmethod
    def current_state(self) -> float:
        """
        :return: the current state of things
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, value: float):
        """
        :param value: make the thing do its thing
        :return:
        """
        raise NotImplementedError


# pylint: disable=R0902
class NumberEntity(CommandEntity):
    """
    Manages a number entity.
    """

    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        handler: NumberHandler,
        device_class: NumericDevice = NumericDevice.NONE,
        minimum: int = 1,
        maximum: int = 100,
        step: float = 1.0,
        mode: DisplayMode = DisplayMode.AUTO,
        unit_of_measurement: str = None,
    ):
        # pylint: disable=R0913
        """
        Creates a `Number <https://www.home-assistant.io/integrations/number.mqtt/>`_ entity.

        **Note:** the entity must be *started* for it to receive commands and report state.

        :param unique_id: the system-wide id for this entity
        :param name: the "friendly name" of the entity
        :param device: which device it's running on
        :param handler: receives the commands and reports state
        :param device_class: HA-specific -- this lets HA display icons, etc. directly related to
            the entity; defaults to "None"
        :param minimum: minimum number accepted/reported; default 1
        :param maximum: maximum number accepted/reported; default 100
        :param step: allowed "jumps" between the maximum and minimum; default 1.0
        :param mode: how HA displays the number; default *AUTO*
        :param unit_of_measurement: what this represents; **note:** if using a *device_class*, this
            must match what HA expects for that class
        """
        super().__init__("number", unique_id, name, device)
        self._class = device_class
        self._handler = handler
        self._mode = mode
        self._min = minimum
        self._max = maximum
        self._step = step
        self._uom = unit_of_measurement
        self.icon = "mdi:numeric"

    # pylint: disable=C0116
    @property
    def discovery(self) -> dict:
        disco = super().discovery
        disco.update(
            {
                "max": self._max,
                "min": self._min,
                "mode": self._mode.value,
                "step": self._step,
            }
        )
        self._class.add_discovery(disco, self._uom)
        return disco

    @property
    def current_state(self) -> str:
        """
        Extracts the state from the handler for reporting to HA.
        :return: current state or *None*
        """
        state = self._handler.current_state
        return str(state) if state is not None else "None"

    def handle_command(self, payload: str):
        """
        Pass an active command to the handler.
        :param payload: the incoming command from HA
        """
        self._handler.set(float(payload))
