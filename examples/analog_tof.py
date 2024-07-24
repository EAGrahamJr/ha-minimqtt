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
Reports the readings from a Time-of-Flight sensor to HA.
"""

import adafruit_vl6180x
import asyncio
import board
import digitalio

from ha_minimqtt.sensors import AnalogSensor, AnalogDevice
from utils import board_i2c, my_device, EXAMPLES_TOPIC, wrapper

sensor = AnalogSensor(
    "tof_range",
    "Test Range",
    my_device,
    AnalogDevice.DISTANCE,
    unit_of_measurement="cm",
    suggested_precision=1,
)
sensor.set_topic_prefix(EXAMPLES_TOPIC)


async def read_sensor():
    i2c = board_i2c()
    tof_sensor = adafruit_vl6180x.VL6180X(i2c)

    while True:
        mm = tof_sensor.range
        print(f"Range: {mm}mm")
        lux1 = tof_sensor.read_lux(adafruit_vl6180x.ALS_GAIN_1)
        lux10 = tof_sensor.read_lux(adafruit_vl6180x.ALS_GAIN_10)
        print(f"Lux 1x - {lux1} 10x - {lux10}")

        sensor.set_current_state(float(mm / 10.0))

        await asyncio.sleep(0.1)


async def read_button_because_i_dont_like_crtl_c():
    button = digitalio.DigitalInOut(board.BUTTON)
    button.switch_to_input(pull=digitalio.Pull.UP)  # makes it "backwards"
    while button.value:
        await asyncio.sleep(1)


async def main():
    await wrapper.start()
    sensor.start(wrapper)

    ignored = asyncio.create_task(read_sensor())

    await read_button_because_i_dont_like_crtl_c()


asyncio.run(main())
