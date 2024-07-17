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

"""
These are intended to provide backup options for being able to run this library
on microcontrollers **and** "desktop" computers.
"""

# pylint: disable=R0903,W0611
try:
    from socket import gethostname
except ImportError:

    def gethostname():
        """
        Fake
        :return: localhost
        """
        return "localhost"


try:
    from typing import List
except ImportError:

    class List:
        """
        Fake
        """


try:
    import logging
except ImportError:
    import adafruit_logging as logging


class ConstantList:
    """
    Uses reflection to check for what's been defined. Typically, the class would be:

    | class Foo(ConstantList) {
    |    BAR = "bar"
    |    BAZ = "baz"
    | }

    """

    @classmethod
    def list(cls):
        """
        Get a list of the (supposedly) string attributes of the *child* class.
        :return: the string things (see above)
        """
        things = list(
            filter(
                lambda s: not s.endswith("__")
                and not s.startswith("_")
                and s != "list",
                dir(cls),
            )
        )
        # now, run through that and pull out the string things
        name_list = []
        for thing in things:
            attr = getattr(cls, thing)
            if isinstance(attr, str):
                name_list.append(attr)
        return name_list
