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
Common color functions
"""

import math


def rgb_to_xyz(**kwargs) -> tuple:
    """
    Convert RGB to X,Y,X coordinates

    Parameters are r,g,b as ints, or color as a tuple
    :param r: red 0-255
    :param g: green 0-255
    :param b: blue 0-255
    :param color: tuple of (r,g,b)
    :return: the color coordinates
    """
    (r, g, b) = parse_color(**kwargs)

    # Normalize RGB values to the range 0-1
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    # Apply gamma correction
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # Convert to XYZ using the sRGB color space
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return x, y, z


def xyz_to_xy(x, y, z) -> tuple:
    """
    Calculate the chromaticity coordinates.

    :param x: color X component
    :param y: color Y component
    :param z: color Z component
    """
    total = x + y + z
    if total == 0:
        return 0, 0
    return x / total, y / total


def xy_to_cct(x, y) -> int:
    """
    Approximate the CCT  using the McCamy formula.

    :param x: color X component
    :param y: color Y component
    :return: light "temperature" in Kelvin
    """
    n = (x - 0.3320) / (0.1858 - y)
    cct = 449 * (n ** 3) + 3525 * (n ** 2) + 6823.3 * n + 5520.33
    return round(cct)


def cct_to_mireds(cct: int) -> int:
    """
    Convert CCT (Kelvin) to Mireds

    :param cct: degrees
    :return: mireds
    """
    return round(1_000_000 / cct)


def cct_to_rgb(temp: int):
    """
    Convert (roughly) CCT (Kelvin) to RGB
    :param temp: degrees
    :return: tuple of R,G,B
    """

    temp = max(1000, min(temp, 40000)) / 100.0

    if temp <= 66.0:
        red = 255.0
        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if temp <= 19.0:
            blue = 0.0
        else:
            blue = temp - 10.0
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
    else:
        red = temp - 60.0
        red = 329.698727446 * (red ** -0.1332047592)
        green = temp - 60.0
        green = 288.1221695283 * (green ** -0.0755148492)
        blue = 255.0

    return (__color_limit(red), __color_limit(green), __color_limit(blue))


def __color_limit(value):
    return max(0, min(255, int(value)))


def mireds_to_cct(mireds: int) -> int:
    """
    Convert mireds to CCT (Kelvin)
    :param mireds: mireds
    :return: degrees kelvin
    """
    return round(1_000_000 / mireds)


def rgb_to_mireds(**kwargs) -> int:
    """
    Translate RGB to mireds (by way of some other things)

    Parameters are r,g,b as ints, or color as a tuple
    :param r: red 0-255
    :param g: green 0-255
    :param b: blue 0-255
    :param color: tuple of (r,g,b)
    :return: mireds
    """
    x, y, z = rgb_to_xyz(**kwargs)
    if x == 0 and y == 0 and z == 0:
        return 0
    xy_x, xy_y = xyz_to_xy(x, y, z)
    cct = xy_to_cct(xy_x, xy_y)
    mireds = cct_to_mireds(cct)
    return mireds


def rgb_to_brightness(**kwargs) -> int:
    """
    Averages the relative brightness of the color components.

    Parameters are r,g,b as ints, or color as a tuple
    :param r: red 0-255
    :param g: green 0-255
    :param b: blue 0-255
    :param color: tuple of (r,g,b)
    :return: simple "average" of relative color ratios as a "brightness"
    """
    (r, g, b) = parse_color(**kwargs)

    return round((r + g + b) / 3)


def parse_color(**kwargs):
    """
    Parse out named args for colors
    :param kwargs: r,g,b as *int* or a tuple of the same
    :return:  a tuple of RGB
    """
    # tuplize and/or check
    r = kwargs.get("r")
    g = kwargs.get("g")
    b = kwargs.get("b")

    if r is not None and g is not None and b is not None:
        return (r, g, b)

    colors = kwargs.get("color")
    if colors:
        return colors
    raise ValueError(f"Invalid input for colors {kwargs}")
