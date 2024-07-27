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
Defines basic lighting entities.
"""

import json

from ha_minimqtt import ConstantList, CommandHandler, BaseEntity, DeviceIdentifier
from ha_minimqtt._compatibility import List, logging
from ha_minimqtt.color_util import (
    mireds_to_cct,
    rgb_to_brightness,
    rgb_to_mireds,
    cct_to_rgb,
)

class ColorMode(ConstantList):
    """
    Supported modes.
    See https://www.home-assistant.io/integrations/light.mqtt/#supported_color_modes
    """

    ONOFF = "onoff"
    BRIGHTNESS = "brightness"
    COLOR_TEMP = "color_temp"
    HUE_SAT = "hs"
    XY = "xy"
    RGB = "rgb"
    RGBW = "rgbw"
    RGBWW = "rgbww"
    WHITE = "white"

    DOES_COLOR = {RGB, RGBW, RGBWW}
    DOES_BRIGHTNESS = DOES_COLOR.union({BRIGHTNESS, HUE_SAT, XY})

    @staticmethod
    def validate(supports: List[str]):
        """
        Validate the supports list against the known value s
        :param supports:
        :return:
        """
        if ColorMode.ONOFF in supports or ColorMode.BRIGHTNESS in supports:
            if len(supports) > 1:
                raise ValueError(
                    "If 'onoff' or 'brightness' are used, that must be the only value in the list."
                )

        for s in supports:
            if s not in ColorMode.list():
                raise ValueError("'s' is not a supported color mode.")
            # Temporarily not allow some stuff
            if s in (ColorMode.HUE_SAT, ColorMode.XY, ColorMode.WHITE):
                raise ValueError("'s' is currently not supported.")
        # only allow one of RGB, RGBW, or RGBWW?

# pylint: disable=W0223,W1203
class LightHandler(CommandHandler):
    """
    Handles basic lighting interface.

    Because HA is using complex JSON objects, this class basically handles the parsing of the
    messages. Child-implementations of **this** class should fill in the missing details, obviously.
    """

    def __init__(self, supports: List[str], effects: List[str] = None):
        """
        Create a basic handler that supports color modes.

        :param supports: the color modes supported
        :param effects: an optional list of "special effects" that can be produced
        """
        ColorMode.validate(supports)
        self._supports = list(supports)
        self._effects = list(effects) if effects else None
        self._current_effect = None
        self._logger = logging.getLogger("LightHandler")

    def add_to_discovery(self, disco: dict) -> dict:
        disco["supported_color_modes"] = self._supports
        if self._supports != ColorMode.ONOFF:
            disco["brightness"] = True
        if self._effects:
            disco["effects"] = True
            disco["effect_list"] = self._effects

        return disco

    def current_state(self) -> str:
        """
        Lights return a complex JSON payload, so try to get as much info here

        :return: JSON payload as string
        """

        # if effects are supported, which one is running?
        if self._effects and self._current_effect:
            status = {"effect": self._current_effect, "state": "ON"}

        # otherwise more "boring" stuff
        else:
            status = {"state": "ON" if self._is_on() else "OFF"}

            if ColorMode.BRIGHTNESS in self._supports:
                status["brightness"] = self._get_brightness()
                status["color_mode"] = ColorMode.BRIGHTNESS

            elif any(s in self._supports for s in ColorMode.DOES_COLOR):
                status["color_mode"] = ColorMode.RGB
                (r, g, b) = self._get_color()
                colors = {"r": r, "g": g, "b": b}
                status["color"] = colors

                # optionally allow for a brightness status value
                try:
                    status["brightness"] = self._get_brightness()
                except NotImplementedError:
                    pass

                # a lot of RGB stuff will also support temperatures,
                # so add it if available or calculate
                if ColorMode.COLOR_TEMP in self._supports:
                    status["color_temp"] = self._get_color_temp()
                else:
                    status["color_temp"] = rgb_to_mireds(color=(r, g, b))

            elif ColorMode.COLOR_TEMP in self._supports:
                status["color_mode"] = ColorMode.COLOR_TEMP
                status["color_temp"] = self._get_color_temp()

                # optionally allow for a brightness status value
                try:
                    status["brightness"] = self._get_brightness()
                except NotImplementedError:
                    pass
            elif ColorMode.HUE_SAT in self._supports:
                pass
            elif ColorMode.XY in self._supports:
                pass
            else:
                raise ValueError("Unknown color mode to report")

        # turn it into JSON and return
        dumps = json.dumps(status)
        self._logger.debug(f"Sending status: {dumps}")
        return dumps

    def handle_command(self, payload: str):
        """
        Parse the command and try to figure out what to do.
        :param payload: the JSON command payload
        """
        self._logger.debug(f"Received payload: {payload}")
        command = json.loads(payload)

        # effects have basic priority here
        if self._effects and "effect" in command:
            self._current_effect = command["effect"]
            self._execute_effect(self._current_effect)
        # otherwise boring stuff
        else:
            if "color" in command:
                colors = command["color"]
                if "r" in colors and "g" in colors and "b" in colors:
                    self._set_color(r=colors["r"], g=colors["g"], b=colors["b"])
                else:
                    self._logger.warning(f"Unknown colors: {colors}")
            elif "color_temp" in command:
                mireds = command["color_temp"]
                self._set_color_temp(mireds)
            elif "brightness" in command:
                self._set_brightness(command["brightness"])
            elif "state" in command:
                self._set_on(command["state"] == "ON")

    def _is_on(self) -> bool:
        """
        :return: True if *on*, False otherwise
        """
        raise NotImplementedError("No value")

    def _set_on(self, on: bool):
        """
        :param on: True if *on*, False otherwise
        """
        raise NotImplementedError("Needs implementation")

    def _get_brightness(self) -> int:
        """
        :return: how bright the light is (0-255)
        """
        raise NotImplementedError("No value")

    def _set_brightness(self, bright: int) -> int:
        """
        :param bright: how bright the light is (0-255)
        """
        raise NotImplementedError("Requires value 0-255")

    def _get_color(self) -> tuple:
        """
        :return: the current color in as a tuple of (red, green, blue)
        """
        raise NotImplementedError("No value")

    def _set_color(self, **kwargs):
        """
        Sets color

        Parameters are r,g,b as ints, or color as a tuple. Implementations may want to use
        the parse *_parse_color* function.
        :param r: red 0-255
        :param g: green 0-255
        :param b: blue 0-255
        :param color: tuple of (r,g,b)
        """
        raise NotImplementedError("Requires values of r,g,b values 0-255")

    def _get_color_temp(self) -> int:
        """
        :return: the current color temperature in nireds
        """
        raise NotImplementedError("Requires a temperature in Kelvin")

    def _set_color_temp(self, temp: int):
        """
        :param temp: the color temperature in mireds
        """
        raise NotImplementedError("Requires a temperature in Kelvin")

    def _execute_effect(self, effect: str):
        """
        :param effect: do this thing -- **might** be blocking
        """
        raise NotImplementedError("Needs support")


class LightEntity(BaseEntity):
    """
    Anywhere from simeple on/off to sophisticated effects, based on the controller.
    """

    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        handler: LightHandler,
    ):
        if not handler:
            raise ValueError("'handler' must be defined")

        super().__init__("light", unique_id, name, device, handler)


class RGBHandler(LightHandler):
    """
    Since most micro-controlled LEDs fall into this category, wrap up some common stuff.

    Because this class can't keep track of color settings, implementations may want to over-ride
    the "on" setting to use a "last color" or similar concept.
    """

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    MODES = [ColorMode.RGB, ColorMode.COLOR_TEMP]

    def __init__(self, effects: List[str] = None):
        """
        Sets color mode to RGB and temp (brightness and off/on assumed via HA)
        :param effects:
        """
        super().__init__(self.MODES, effects)

    def _is_on(self) -> bool:
        return self._get_brightness() != 0 and self._get_color() != self.BLACK

    def _set_on(self, on: bool):
        self._set_color(color=self.WHITE if on else self.BLACK)

    def _get_brightness(self) -> int:
        return rgb_to_brightness(color=self._get_color())

    def _set_brightness(self, bright: int):
        # adjust the current color or, if off, based on white
        adjust_this = self._get_color() if self._is_on() else self.WHITE
        adjust_by = bright / 255.0
        r = round(adjust_this[0] * adjust_by)
        g = round(adjust_this[1] * adjust_by)
        b = round(adjust_this[2] * adjust_by)
        self._set_color(color=(r, g, b))

    def _get_color_temp(self) -> int:
        return rgb_to_mireds(color=self._get_color())

    def _set_color_temp(self, temp: int):
        k = mireds_to_cct(temp)
        color = cct_to_rgb(k)
        self._set_color(color=color)
