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

#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
try:
    from typing import List
except ImportError:
    pass

from base import CommandEntity, DeviceIdentifier


class SelectHandler:
    """
    Defines a class that handles selection options.
    """

    @property
    def options(self) -> List[str]:
        raise NotImplementedError

    def execute_option(self, select: str) -> None:
        raise NotImplementedError


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
        super().__init__("select", unique_id, name, device)
        self._handler = handler
        self.icon = "mdi:list-status"
        self._last_option = None

    @property
    def discovery(self) -> dict:
        disco = super().discovery
        disco["options"] = self._handler.options
        return disco

    def current_state(self) -> str:
        return "None" if self._last_option is None else self._last_option

    def handle_command(self, payload: str) -> None:
        self._handler.execute_option(payload)
        self._last_option = payload
