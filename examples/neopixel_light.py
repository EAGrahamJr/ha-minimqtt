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

import board
import neopixel
import asyncio

from ha_minimqtt.cp_device import NeoPixelHandler
from ha_minimqtt.lights import LightEntity
from utils import my_device, EXAMPLES_TOPIC, wrapper

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

entity = LightEntity("test_pixel", "Pixie", my_device, NeoPixelHandler(pixels))
entity.set_topic_prefix(EXAMPLES_TOPIC)


async def read_button_because_i_dont_like_crtl_c():
    import board, digitalio

    button = digitalio.DigitalInOut(board.BUTTON)
    button.switch_to_input(pull=digitalio.Pull.UP)  # makes it "backwards"
    while button.value:
        await asyncio.sleep(1)


async def main():
    await wrapper.start()
    entity.start(wrapper)
    await read_button_because_i_dont_like_crtl_c()


asyncio.run(main())
