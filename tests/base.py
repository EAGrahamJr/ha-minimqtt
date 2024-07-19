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

import json
import unittest

from ha_minimqtt import DeviceIdentifier

TEST_DEVICE = DeviceIdentifier("Kobots", "tests")


class TestBase(unittest.TestCase):
    command_handler = None

    def start_checks(self, device, wrapper) -> dict:
        device.start(wrapper)
        on_connect_method = wrapper.method_calls[0]
        ha_subscribe_method = wrapper.method_calls[2]

        self.assertEqual(
            "homeassistant/status",
            ha_subscribe_method.args[0],
            msg="First sub should be for HA status",
        )
        # this should "trigger" discovery
        on_connect_method.args[0](False)

        # check subscribe to comannd topic
        if device._command_handler:
            sub_command_method = wrapper.method_calls[3]
            self.assertEqual("subscribe", sub_command_method[0])
            self.assertEqual(
                f"{device._topic_prefix}/{device._unique_id}/set",
                sub_command_method.args[0],
            )
            self.command_handler = sub_command_method.args[1]
            publish_disco_method = wrapper.method_calls[4]
        else:
            publish_disco_method = wrapper.method_calls[3]

        self.assertEqual("publish", publish_disco_method[0])
        self.assertEqual(
            publish_disco_method.args[0],
            f"homeassistant/{device._component}/{device._unique_id}/config",
        )
        disco = json.loads(publish_disco_method.args[1])
        # print(disco)

        self.assertEqual(device._name, disco["name"])
        self.assertEqual(device._unique_id, disco["unique_id"])
        self.assertEqual("json", disco["schema"])
        if "sensor" in device._component:
            self.assertEqual("diagnostic", disco["entity_category"])
        else:
            self.assertEqual("config", disco["entity_category"])
        self.assertEqual(
            f"{device._topic_prefix}/{device._unique_id}/state", disco["state_topic"]
        )

        self.assertEqual("tests", disco["device"]["model"])
        self.assertEqual("Kobots", disco["device"]["manufacturer"])
        self.assertTrue(device._unique_id in disco["device"]["identifiers"])
        dc = device._device_class
        if dc and dc.isa_device():
            self.assertEqual(dc._device_class.lower(), disco["device_class"])
            if dc._unit_of_measurement:
                self.assertEqual(dc._unit_of_measurement, disco["unit_of_measurement"])

        wrapper.reset_mock()
        return disco

    def create_basic_device(self):
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
