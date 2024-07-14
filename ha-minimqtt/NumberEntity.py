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
from enum import Enum

from base import CommandEntity, DeviceIdentifier, DeviceClass

try:
    from abc import ABC, abstractmethod
except ImportError:
    pass


class NumericDevice(DeviceClass):
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
        raise NotImplementedError

    @abstractmethod
    def set(self, value: float):
        raise NotImplementedError


class NumberEntity(CommandEntity):
    """
    Manages a number entity.

    A "handler" is attached to manage status and commands.
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
        super().__init__("number", unique_id, name, device)
        self._class = device_class
        self._handler = handler
        self._mode = mode
        self._min = minimum
        self._max = maximum
        self._step = step
        self._uom = unit_of_measurement
        self.icon = "mdi:numeric"

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

    def current_state(self) -> str:
        state = self._handler.current_state
        return str(state) if state is not None else "None"

    def handle_command(self, payload: str):
        self._handler.set(float(payload))