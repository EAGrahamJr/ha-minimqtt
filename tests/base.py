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

        first_publish = None
        ha_subscribe_method = None
        ha_command_method = None
        on_connect_method = None
        on_disconnect_method = None

        for m in wrapper.method_calls:
            name = str(m)
            if "call.publish" in name:
                first_publish = m
            elif "call.subscribe" in name:
                if "homeassistant/status" in name:
                    ha_subscribe_method = m
                else:
                    ha_command_method = m
            elif "call.add_connect_listener" in name:
                on_connect_method = m
            elif "call.add_disconnect_listener" in name:
                on_disconnect_method = m

        # print(f"debug this {wrapper.method_calls}")

        self.assertEqual(
            "homeassistant/status",
            ha_subscribe_method.args[0],
            msg="First sub should be for HA status",
        )
        # this should "trigger" discovery
        on_connect_method.args[0](False)

        # check subscribe to comannd topic
        if device._command_handler:
            self.assertEqual(
                f"{device._topic_prefix}/{device._unique_id}/set",
                ha_command_method.args[0],
            )
            self.command_handler = ha_command_method.args[1]

        # self.assertEqual("publish", publish_disco_method[0])
        self.assertEqual(
            first_publish.args[0],
            f"homeassistant/{device._component}/{device._unique_id}/config",
        )
        disco = json.loads(first_publish.args[1])
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
