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

import unittest
from unittest import TestCase
from unittest.mock import patch
from ha_minimqtt.mqttwrapper import MQTTClientWrapper
from ha_minimqtt.sensors import AnalogSensor,BinarySensor
from ha_minimqtt import DeviceIdentifier
import json

TEST_DEVICE = DeviceIdentifier("Kobots","tests")

class AnalogSensorTestCase(TestCase):
    @patch.object(MQTTClientWrapper,"add_connect_listener")
    def test_discovery_message(self,wrapper):
        sensor = AnalogSensor("id2","AS",TEST_DEVICE)
        sensor.start(wrapper)
        on_connect_method = wrapper.method_calls[0]
        ha_subscribe_method = wrapper.method_calls[2]
        self.assertEqual("homeassistant/status", ha_subscribe_method.args[0])
        # this should "trigger" discovery
        on_connect_method.args[0](False)
        publish_disco_method = wrapper.method_calls[3]
        self.assertEqual(publish_disco_method[0],"publish")
        self.assertEqual(f"homeassistant/sensor/{sensor.unique_id}/config",
                         publish_disco_method.args[0])
        config = json.loads(publish_disco_method.args[1])
        self.assertEqual("tests", config["device"]["model"])

class BinarySensorTestCase(TestCase):
    @patch.object(MQTTClientWrapper,"add_connect_listener")
    def test_discovery_message(self,wrapper):
        sensor = BinarySensor("id1","BS",TEST_DEVICE)
        sensor.start(wrapper)
        on_connect_method = wrapper.method_calls[0]
        ha_subscribe_method = wrapper.method_calls[2]
        self.assertEqual("homeassistant/status", ha_subscribe_method.args[0])
        # this should "trigger" discovery
        on_connect_method.args[0](False)
        publish_disco_method = wrapper.method_calls[3]
        self.assertEqual(publish_disco_method[0],"publish")
        self.assertEqual(f"homeassistant/binary_sensor/{sensor.unique_id}/config",
                         publish_disco_method.args[0])
        config = json.loads(publish_disco_method.args[1])
        self.assertEqual("tests", config["device"]["model"])


if __name__ == '__main__':
    unittest.main()
