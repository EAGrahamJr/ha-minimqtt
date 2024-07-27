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
Classes for Adafruit CircuitPython specific integrations.
"""
import adafruit_pixelbuf

from ha_minimqtt.color_util import parse_color
from ha_minimqtt.lights import RGBHandler

# pylint: disable=W0223:
class NeoPixelHandler(RGBHandler):
    """
    A handler for "Neopixels" (WS28xx) like things and/or any of the
    Adafruit *pixelbuf* implementations.
    """

    _last_brightness = 0
    _last_color = None
    _on_off = False

    def __init__(self, pixelbuf: adafruit_pixelbuf.PixelBuf):
        """
        Make the handler.
        :param pixelbuf: the pixelbuf to address
        """
        super().__init__()
        self._pixels = pixelbuf
        self._pixels.fill(self.BLACK)
        self._pixels.brightness = 0
        self._last_color = self.BLACK

        # pass on special effects for now

    def _is_on(self) -> bool:
        return self._on_off

    def _set_on(self, on: bool):
        if on:
            # when turning it on, if "first time", bring it all the way on
            if self._last_color == self.BLACK:
                self._last_color = self.WHITE
            self._pixels.fill(self._last_color)
            if self._pixels.brightness == 0:
                self._pixels.brightness = 1
        else:
            self._pixels.fill(self.BLACK)
        self._on_off = on

    def _get_brightness(self) -> int:
        return round(self._pixels.brightness * 255)

    def _set_brightness(self, bright: int):
        # no color, make it white
        if self._last_color == self.BLACK:
            self._last_color = self.WHITE
            self._pixels.fill(self.WHITE)
        self._pixels.brightness = bright / 255.0
        self._on_off = True

    def _get_color(self) -> tuple:
        return self._last_color

    def _set_color(self, **kwargs):
        self._last_color = parse_color(**kwargs)
        self._pixels.fill(self._last_color)
        self._on_off = True
