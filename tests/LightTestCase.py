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
import json

from base import TestBase, TEST_DEVICE
from ha_minimqtt.color_util import (
    parse_color,
)
from ha_minimqtt.mqttwrapper import MQTTClientWrapper
from ha_minimqtt.lights import (
    RGBHandler,
    LightEntity,
)

from time import sleep


# in a class just to make it pretty?
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class TestHandler(RGBHandler):
    _test_state = Colors.BLACK
    effects = ["blink", "pulse", "fade_on", "fade_off"]
    _ce = None

    def __init__(self):
        super().__init__(self.effects)

    def get_color(self) -> tuple:
        return self._test_state

    def set_color(self, **kwargs):
        self._test_state = parse_color(**kwargs)

    def execute_effect(self, effect: str):
        self._ce = effect
        if "fade" in effect:
            sleep(5)


class LightTest(TestBase):
    @staticmethod
    def create_device():
        return LightEntity("night_light", "Night Light", TEST_DEVICE, TestHandler())

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_discovery_payload(self, wrapper):
        disco = self.start_checks(self.create_device(), wrapper)

        # check for additional information
        self.assertTrue(disco["brightness"])
        self.assertEqual(RGBHandler.MODES, disco["supported_color_modes"])
        self.assertTrue(disco["effects"])
        self.assertEqual(TestHandler.effects, disco["effect_list"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_light_on(self, wrapper):
        light = self.create_device()
        self.start_checks(light, wrapper)

        # send a command to the captured handler
        self.command_handler('{"state" : "ON"}')

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(light._status_topic(), sent_status_method.args[0])
        status = json.loads(sent_status_method.args[1])

        self.assertEqual("ON", status["state"])
        self.assertEqual("rgb", status["color_mode"])
        self.assertEqual(255, status["brightness"])
        color = status["color"]
        self.assertEqual(255, color["r"])
        self.assertEqual(255, color["g"])
        self.assertEqual(255, color["b"])
        self.assertLess(150, status["color_temp"])
        self.assertGreater(160, status["color_temp"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_light_dimmed(self, wrapper):
        light = self.create_device()
        self.start_checks(light, wrapper)

        # send a command to the captured handler
        self.command_handler('{"brightness" : 128}')

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(light._status_topic(), sent_status_method.args[0])
        status = json.loads(sent_status_method.args[1])

        self.assertEqual("ON", status["state"])
        self.assertEqual("rgb", status["color_mode"])
        self.assertEqual(128, status["brightness"])
        color = status["color"]
        self.assertEqual(128, color["r"])
        self.assertEqual(128, color["g"])
        self.assertEqual(128, color["b"])
        self.assertIn(status["color_temp"], range(150, 160))
        # self.assertLess(150, )
        # self.assertGreater(160, status["color_temp"])

    @patch.object(MQTTClientWrapper, "add_connect_listener")
    def test_light_set_temp(self, wrapper):
        # Note: varying aglorightms produce slightly different rounding errors, so ranges are
        # checked here
        light = self.create_device()
        self.start_checks(light, wrapper)

        # send a command to the captured handler
        self.command_handler('{"color_temp" : 370}')

        # did the status fire?
        sent_status_method = wrapper.method_calls[0]
        wrapper.reset_mock()
        self.assertEqual("publish", sent_status_method[0])
        self.assertEqual(light._status_topic(), sent_status_method.args[0])
        status = json.loads(sent_status_method.args[1])

        self.assertEqual("ON", status["state"])
        self.assertEqual("rgb", status["color_mode"])
        self.assertIn(status["brightness"], range(165, 170))
        color = status["color"]
        self.assertEqual(255, color["r"])
        self.assertIn(color["g"], range(163, 169))
        self.assertIn(color["b"], range(85, 90))
        self.assertIn(status["color_temp"], range(365, 395))
