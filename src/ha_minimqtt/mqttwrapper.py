# MIT License
#
# Copyright (c) 2024 E. A. (Ed) Graham, Jr.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
"Wrappers" (decorators) for MQTT clients.
"""
from ha_minimqtt.compatibility import Callable


class MQTTClientWrapper:
    """
    The basic wrapper definition.
    """

    def add_connect_listener(self, callback: Callable[[bool], None]) -> None:
        """
        Add a callback for when the client is (re-)connected to the broker.

        :param callback: call me
        """
        raise NotImplementedError

    def add_disconnect_listener(self, callback: Callable[[None], None]) -> None:
        """
        Add a callback for when the client is disconnected from the broker.

        :param callback: call me
        """
        raise NotImplementedError

    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        """
        Subscribes a particular callback method to a topic.

        Note that more than one callback **CAN** be subscribed to a topic. All subscribers will be
        re-subscribed automatically on re-connect.
        :param topic: the topic name
        :param callback: call me when messages arrive
        """
        raise NotImplementedError

    def publish(self, topic: str, payload: str, retain: bool = False, qos: int = 0):
        """
        Pushes a string payload to the topic.

        Dict types should be JSON-ized prior to publication.

        :param topic: the topic
        :param payload: the payload
        :param retain: option to "retain" the message (persistent), default is *False*
        :param qos: option to set delivery QoS, default is *0*
        """
        raise NotImplementedError
