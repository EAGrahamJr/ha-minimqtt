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

from unittest.mock import patch

from base import TestBase, TEST_DEVICE
from ha_minimqtt.mqttwrapper import MQTTClientWrapper
from ha_minimqtt.sensors import AnalogSensor, BinarySensor, AnalogDevice, BinaryDevice


class AnalogSensorTestCase(TestBase):
    def create_basic_device(self):
        return AnalogSensor("id2", "AS", TEST_DEVICE)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_message(self, wrapper):
        device = self.create_basic_device()
        # also set the topic prefix, lest anyone thinks that doesn't work
        device.set_topic_prefix("foo")
        self.start_checks(device, wrapper)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_with_class(self, wrapper):
        device = AnalogSensor(
            "id2", "AS", TEST_DEVICE, AnalogDevice.VOLUME, unit_of_measurement="dB"
        )
        self.start_checks(device, wrapper)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_basic_state(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

        device.set_current_state(50.0)
        sent_status_method = wrapper.method_calls[0]
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("50.0", sent_status_method.args[1])

    def test_invalid_state(self):
        device = self.create_basic_device()
        try:
            device.set_current_state("ralph")
            self.fail("Should have failed to set invalid status")
        except ValueError:
            pass


class BinarySensorTestCase(TestBase):
    def create_basic_device(self):
        return BinarySensor("id1", "BS", TEST_DEVICE)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_message(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_with_class(self, wrapper):
        device = BinarySensor(
            "id2", "BS", TEST_DEVICE, BinaryDevice.BATTERY, off_delay=5
        )
        disco = self.start_checks(device, wrapper)
        self.assertEqual(5, disco["off_delay"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_basic_state(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

        device.set_current_state(True)
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("ON", sent_status_method.args[1])

        device.set_current_state("Off")
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("OFF", sent_status_method.args[1])

    def test_invalid_binary_state(self):
        device = self.create_basic_device()
        try:
            device.set_current_state(50)
            self.fail("Should have failed to set invalid status")
        except ValueError:
            pass
        try:
            device.set_current_state("fail")
            self.fail("Should have failed to set invalid status")
        except ValueError:
            pass
