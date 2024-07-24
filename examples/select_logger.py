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

# Uses a select/option to set logging

import adafruit_logging as logging
import asyncio

from ha_minimqtt._compatibility import List
from ha_minimqtt.select import SelectHandler, SelectEntity
from utils import my_device, EXAMPLES_TOPIC, wrapper


class Selector(SelectHandler):
    _state = "INFO"

    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)

    @property
    def options(self) -> List[str]:
        return ["ERROR", "WARN", "INFO", "DEBUG"]

    def handle_command(self, payload: str):
        self._logger.info(f"Setting wrapper logger to '{payload}'")

        if payload == "ERROR":
            wrapper._logger.setLevel(logging.ERROR)
        elif payload == "WARN":
            wrapper._logger.setLevel(logging.WARNING)
        elif payload == "INFO":
            wrapper._logger.setLevel(logging.INFO)
        elif payload == "DEBUG":
            wrapper._logger.setLevel(logging.DEBUG)
        else:
            self._logger.error(f"Unknown command '{payload}")

    def current_state(self) -> str:
        l = wrapper._logger.getEffectiveLevel()
        if l == logging.ERROR:
            return "ERROR"
        if l == logging.WARNING:
            return "WARN"
        if l == logging.INFO:
            return "INFO"
        if l == logging.DEBUG:
            return "DEBUG"
        return ""


entity = SelectEntity("drop_me", "ESPY 32 Logging Level", my_device, Selector())
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
