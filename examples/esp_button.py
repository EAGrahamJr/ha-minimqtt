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

# uses the BOOT button available on Adafruit QT Py ESP32-S3 boards for a binary input.

import asyncio
import adafruit_logging as logging
import board
import digitalio
from ha_minimqtt import DeviceIdentifier
from ha_minimqtt.cp_mqtt import HAMMFactory
from ha_minimqtt.sensors import BinarySensor,BinaryDevice

wrapper = HAMMFactory.create_wrapper()
wrapper._logger.setLevel(logging.INFO)

identifier = DeviceIdentifier("kobots", "QtPy ESP32 S3", identifier="i-spy")
sensor = BinarySensor("push_me","ESP32 Button",identifier, BinaryDevice.CONNECTIVITY)
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)  # makes it "backwards"

async def main():
    await wrapper.start()
    sensor.start(wrapper)
    while True:
        sensor.set_current_state(not button.value)
        await asyncio.sleep(1)

asyncio.run(main())
