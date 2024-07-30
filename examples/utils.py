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
import adafruit_logging as logging

from ha_minimqtt import DeviceIdentifier
from ha_minimqtt.cp_mqtt import HAMMFactory


# quick and dirty way to get the "default" I2C channel
def board_i2c():
    # Create I2C bus as normal
    print()
    try:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        print("Using I2C")
    except Exception:
        try:
            i2c = (
                board.STEMMA_I2C()
            )  # For using the built-in STEMMA QT connector on a microcontroller
            print("Using STEMMA")
        except Exception:
            print("Unable to locate I2C interface - is anything connected?")
            exit(1)
    return i2c


# topic prefix for MQTT
EXAMPLES_TOPIC = "kobots_ha/examples"

# common "device" for testing/examples
my_device = DeviceIdentifier("kobots", "QtPy ESP32 S3", identifier="i-spy")

# common wrapper
wrapper = HAMMFactory.create_wrapper()
wrapper._logger.setLevel(logging.INFO)
