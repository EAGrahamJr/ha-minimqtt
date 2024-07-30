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
from typing import List

from base import TestBase, TEST_DEVICE
from unittest.mock import patch

from ha_minimqtt import MQTTClientWrapper, SwitchEntity
from ha_minimqtt.number import NumberCommandHandler, NumberEntity, NumericDevice
from ha_minimqtt.select import SelectEntity, SelectHandler


class NumberEntityTest(TestBase):
    # mocked command handler
    class MockHandler(NumberCommandHandler):
        _status = ""

        def __init__(self) -> None:
            super().__init__(minimum=0, maximum=11)

        def handle_command(self, payload: str):
            self._status = payload

        def current_state(self) -> str:
            return self._status

    mock_handler = MockHandler()

    def create_basic_device(self):
        return NumberEntity("ne_1", "Test Servo", TEST_DEVICE, self.mock_handler)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_message(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_with_class(self, wrapper):
        device = NumberEntity(
            "ne_1",
            "Amp Volume",
            TEST_DEVICE,
            self.mock_handler,
            device_class=NumericDevice.VOLUME,
        )
        disco = self.start_checks(device, wrapper)
        self.assertEqual("auto", disco["mode"])

        # TODO these are likely to move to the handler
        self.assertEqual(11, disco["max"])
        self.assertEqual(0, disco["min"])
        self.assertEqual(1.0, disco["step"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_command_received(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

        # note this was pulled from the discovery subscription, so it should react to a "message"
        self.command_handler("50")
        self.assertEqual("50", self.mock_handler.current_state())

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("50", sent_status_method.args[1])


class SelectEntityTest(TestBase):
    class MockHandler(SelectHandler):
        _status = ""

        @property
        def options(self) -> List[str]:
            return ["Yes", "No", "Maybe"]

        def handle_command(self, payload: str):
            self._status = payload

        def current_state(self) -> str:
            return self._status

    mock_handler = MockHandler()

    def create_basic_device(self):
        return SelectEntity("magic_8", "Fortune Thing", TEST_DEVICE, self.mock_handler)

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_message(self, wrapper):
        device = self.create_basic_device()
        disco = self.start_checks(device, wrapper)
        self.assertEqual(self.mock_handler.options, disco["options"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_command_received(self, wrapper):
        device = self.create_basic_device()
        self.start_checks(device, wrapper)

        # note this was pulled from the discovery subscription, so it should react to a "message"
        self.command_handler("Maybe")
        self.assertEqual("Maybe", self.mock_handler.current_state())

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("Maybe", sent_status_method.args[1])


class SwitchEntityTest(TestBase):
    called = False

    def call_me(self, on: bool):
        self.called = on

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_swtich_turned_on(self, wrapper):
        device = SwitchEntity("onner_offer", "Switch", TEST_DEVICE, self.call_me)
        self.start_checks(device, wrapper)

        self.command_handler("ON")
        self.assertEqual("ON", device.current_state())
        self.assertTrue(self.called)

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(device._status_topic(), sent_status_method.args[0])
        self.assertEqual("ON", sent_status_method.args[1])
