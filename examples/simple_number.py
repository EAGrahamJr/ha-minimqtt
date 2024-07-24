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

# uses a "fake" servo to respond to numeric inputs

import asyncio
from ha_minimqtt.number import NumberEntity, NumberCommandHandler
from utils import my_device, EXAMPLES_TOPIC, wrapper


class ServoHandler(NumberCommandHandler):
    _angle = 0.0

    def __init__(self):
        super().__init__(minimum=0, maximum=180)

    def execute(self, value: float) -> float:
        from time import sleep

        self._angle = int(value)
        print(f"Moved to {self._angle}")
        # classic sleep because this is a blocking op
        sleep(0.005)
        return float(self._angle)


# note there is no specific entity class for a thing that swings by degrees
servo_entity = NumberEntity(
    "swinger", "Swinging Thing", my_device, handler, unit_of_measurement="degrees"
)
servo_entity.set_topic_prefix(EXAMPLES_TOPIC)


# and... begin
async def main():
    await wrapper.start()
    servo_entity.start(wrapper)
    while True:
        await asyncio.sleep(0)


asyncio.run(main())
