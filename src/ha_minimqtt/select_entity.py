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
Select entity: reports and responds to a defined of textual commands.
"""

from ha_minimqtt._compatibility import ABC, abstractmethod, List
from ha_minimqtt.base import CommandEntity, DeviceIdentifier


class SelectHandler(ABC):
    """
    Defines a class that handles selection options.
    """

    @property
    @abstractmethod
    def options(self) -> List[str]:
        """
        :return: the list of things this can handle
        """
        raise NotImplementedError

    @abstractmethod
    def execute_option(self, select: str) -> None:
        """
        :param select: execute this command
        """
        raise NotImplementedError


# pylint: disable=C0116
class SelectEntity(CommandEntity):
    """
    Defines an entity that presents a set of "selections" that can be executed by
    the designated handler.
    """

    def __init__(
        self,
        unique_id: str,
        name: str,
        device: DeviceIdentifier,
        handler: SelectHandler,
    ):
        """
        Create a `Select <https://www.home-assistant.io/integrations/select.mqtt/>`_ entity.

         **Note:** the entity must be *started* for it to receive commands and report state.

        :param unique_id: the system-wide id for this entity
        :param name: the "friendly name" of the entity
        :param device: which device it's running on
        :param handler: receives the commands and reports state
        """
        super().__init__("select", unique_id, name, device)
        self._handler = handler
        self.icon = "mdi:list-status"
        self._last_option = None

    @property
    def discovery(self) -> dict:
        disco = super().discovery
        disco["options"] = self._handler.options
        return disco

    @property
    def current_state(self) -> str:
        """
        :return: the last option set or *None*
        """
        return "None" if self._last_option is None else self._last_option

    def handle_command(self, payload: str) -> None:
        """
        Passes the command on to the handler and retains it as the "last set" for status.
        :param payload: the command
        """
        self._handler.execute_option(payload)
        self._last_option = payload
