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
# 3
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

from ha_minimqtt._compatibility import List
from ha_minimqtt import BaseEntity, DeviceIdentifier, CommandHandler


class SelectHandler(CommandHandler):
    """
    Defines a class that handles selection options.
    """

    @property
    def options(self) -> List[str]:
        """
        :return: the list of things this can handle
        """
        raise NotImplementedError


class SelectEntity(BaseEntity):
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
        if not handler:
            raise ValueError("'handler' must be defined")
        super().__init__("select", unique_id, name, device, handler)
        self.icon = "mdi:list-status"
        self._command_options = handler.options

    def _add_other_discovery(self, disco: dict) -> dict:
        disco["options"] = self._command_options
        return disco
