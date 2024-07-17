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
from ha_minimqtt._compatibility import ConstantList
from ha_minimqtt import (
    BaseEntity,
    DeviceIdentifier,
    DeviceClass,
    NumberDisplayMode,
    CommandHandler,
)

# pylint: disable=R0801


class NumericDevice(DeviceClass, ConstantList):
    """
    The various things HA knows about for numbers. See `Device class
    <https://www.home-assistant.io/integrations/number/#device-class>`_
    """

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


class NumberEntity(BaseEntity):
    """
    Manages a number entity.
    """

    # pylint: disable=R0913
    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        handler: CommandHandler,
        device_class: str = NumericDevice.NONE,
        minimum: int = 1,
        maximum: int = 100,
        step: float = 1.0,
        mode: str = NumberDisplayMode.AUTO,
        unit_of_measurement: str = None,
    ):
        """
        Creates a `Number <https://www.home-assistant.io/integrations/number.mqtt/>`_ entity.

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
        if not handler:
            raise ValueError("'handler' must be defined")
        if device_class and device_class not in NumericDevice.list():
            raise ValueError(
                f"'device_class' {device_class} must be in the list of supported types."
            )
        if mode and mode not in NumberDisplayMode.list():
            raise ValueError(f"'mode' {mode} must be in the list of supported types.")

        super().__init__(
            "number",
            unique_id,
            name,
            device,
            handler,
            NumericDevice(device_class, unit_of_measurement),
        )

        self._mode = mode
        self._min = minimum
        self._max = maximum
        self._step = step
        self.icon = "mdi:numeric"

    def _add_other_discovery(self, disco: dict) -> dict:
        disco.update(
            {
                "max": self._max,
                "min": self._min,
                "mode": self._mode,
                "step": self._step,
            }
        )
        return disco
