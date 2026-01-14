"""
Colors for coding artists

*New in 0.7.0*

---

Copyright (c) 2025-2026 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""

from __future__ import annotations

from collections import namedtuple
from functools import lru_cache
import math

from suou.functools import deprecated
from suou.mat import Matrix


class Chalk:
    """
    ANSI escape codes for terminal colors, similar to JavaScript's `chalk` library.

    Best used with Python 3.12+ that allows arbitrary nesting of f-strings.

    Yes, I am aware colorama exists.

    UNTESTED

    *New in 0.7.0*
    """
    CSI = '\x1b['
    RED = CSI + "31m"
    GREEN = CSI + "32m"
    YELLOW = CSI + "33m"
    BLUE = CSI + "34m"
    CYAN = CSI + "36m"
    PURPLE = CSI + "35m" 
    GREY = CSI + "90m"
    END_COLOR = CSI + "39m"
    BOLD = CSI + "1m"
    END_BOLD = CSI + "22m"
    FAINT = CSI + "2m"
    def __init__(self, flags = (), ends = ()):
        self._flags = tuple(flags)
        self._ends = tuple(ends)
    @lru_cache()
    def _wrap(self, beg, end):
        return Chalk(self._flags + (beg,), self._ends + (end,))
    def __call__(self, s: str) -> str:
        return ''.join(self._flags) + s + ''.join(reversed(self._ends))
    @property
    def red(self):
        return self._wrap(self.RED, self.END_COLOR)
    @property
    def green(self):
        return self._wrap(self.GREEN, self.END_COLOR)
    @property
    def blue(self):
        return self._wrap(self.BLUE, self.END_COLOR)
    @property
    def yellow(self):
        return self._wrap(self.YELLOW, self.END_COLOR)
    @property
    def cyan(self):
        return self._wrap(self.CYAN, self.END_COLOR)
    @property
    def purple(self):
        return self._wrap(self.PURPLE, self.END_COLOR)
    @property
    def grey(self):
        return self._wrap(self.GREY, self.END_COLOR)
    gray = grey
    marine = blue
    magenta = purple
    @property
    def bold(self):
        return self._wrap(self.BOLD, self.END_BOLD)
    @property
    def faint(self):
        return self._wrap(self.FAINT, self.END_BOLD)


## TODO make it lazy / an instance variable?
chalk = Chalk()


## Utilities for web colors

class RGBColor(namedtuple('_WebColor', 'red green blue')):
    """
    Representation of a color in the sRGB / TrueColor (0 to 255) space.

    Useful for theming.

    *Changed in 0.12.0*: name is now RGBColor, with WebColor being an alias.
    Added conversions to and from OKLCH, OKLab, sRGB, and XYZ.
    """
    def lighten(self, *, factor = .75):
        """
        Return a whitened shade of the color.
        Factor stands between 0 and 1: 0 = total white, 1 = no change. Default is .75
        """
        return WebColor(
            255 - int((255 - self.red) * factor),
            255 - int((255 - self.green) * factor),
            255 - int((255 - self.blue) * factor),
        )
    def darken(self, *, factor = .75):
        """
        Return a darkened shade of the color.
        Factor stands between 0 and 1: 0 = total black, 1 = no change. Default is .75
        """
        return WebColor(
            int(self.red * factor),
            int(self.green * factor),
            int(self.blue * factor)
        )
    def greyen(self, *, factor = .75):
        """
        Return a desaturated shade of the color.
        Factor stands between 0 and 1: 0 = gray, 1 = no change. Default is .75
        """
        return self.darken(factor=factor) + self.lighten(factor=factor)
        
    def blend_with(self, other: RGBColor):
        """
        Mix two colors, returning the average.
        """
        return RGBColor (
            (self.red + other.red) // 2,
            (self.green + other.green) // 2,
            (self.blue + other.blue) // 2
        )

    def to_linear_rgb(self):
        """
        Convert to linear RGB space.

        *New in 0.12.0*
        """
        return LinearRGBColor(*(
            ((i / 255) / 12.92 if abs(i / 255) <= 0.04045 else 
            (-1 if i < 0 else 1) * (((abs(i / 255) + 0.055)) / 1.055) ** 2.4) for i in self
        ))

    def to_oklab(self):
        return self.to_linear_rgb().to_oklab()

    __add__ = blend_with

    def __str__(self):
        return f"rgb({self.red}, {self.green}, {self.blue})"

    def to_xyz(self):
        return self.to_linear_rgb().to_xyz()

    def to_oklch(self):
        return self.to_linear_rgb().to_oklch()

    
WebColor = RGBColor

## The following have been adapted from 
## https://gist.github.com/dkaraush/65d19d61396f5f3cd8ba7d1b4b3c9432

class LinearRGBColor(namedtuple('_LRGBColor', 'red green blue')):
    """
    Represent a color in the linear RGB space.

    *New in 0.12.0*
    """ 
    red: float
    green: float
    blue: float
    
    def __str__(self):
        r, g, b = round(self.red, 4), round(self.green, 4), round(self.blue, 4)

        return f"linear-rgb({r}, {g}, {b})"
    
    def to_rgb(self):
        return RGBColor(*(
            ((-1 if i < 0 else 1) * int(255 * (1.055 * (abs(i) ** (1/2.4)) - 0.055))
            if abs(i) > 0.0031308 else int(255 * (12.92 * i))) for i in self))

    LRGB_TO_XYZ = Matrix([
        [0.41239079926595934, 0.357584339383878,   0.1804807884018343],
        [0.21263900587151027, 0.715168678767756,   0.07219231536073371],
        [0.01933081871559182, 0.11919477979462598, 0.9505321522496607]
    ])
    
    def to_xyz(self):
        return XYZColor(*(self.LRGB_TO_XYZ @ Matrix.as_column([x for x in self])).get_column())

    def to_oklab(self):
        return self.to_xyz().to_oklab()

    def to_oklch(self):
         return self.to_xyz().to_oklch()
    

class XYZColor(namedtuple('_XYZColor', 'x y z')):
    """
    Represent a color in the XYZ color space.

    *New in 0.12.0*
    """

    XYZ_TO_LRGB = Matrix([
        [ 3.2409699419045226,  -1.537383177570094,   -0.4986107602930034],
        [-0.9692436362808796,   1.8759675015077202,  0.04155505740717559],
        [ 0.05563007969699366, -0.20397695888897652,  1.0569715142428786]
    ])

    XYZ_TO_LMS = Matrix([
        [0.8190224379967030, 0.3619062600528904, -0.1288737815209879],
        [0.0329836539323885, 0.9292868615863434,  0.0361446663506424],
        [0.0481771893596242, 0.2642395317527308,  0.6335478284694309]
    ])

    LMSG_TO_OKLAB = Matrix([
        [0.2104542683093140,  0.7936177747023054, -0.0040720430116193],
        [1.9779985324311684, -2.4285922420485799,  0.4505937096174110],
        [0.0259040424655478,  0.7827717124575296, -0.8086757549230774]
    ])

    def to_linear_rgb(self):
        return LinearRGBColor(*[x for x in (self.XYZ_TO_LRGB @ Matrix.as_column(self)).get_column()])

    def to_rgb(self):
        return self.to_linear_rgb().to_rgb()
    
    def to_oklab(self):
        lms = (self.XYZ_TO_LMS @ Matrix.as_column(self)).get_column()
        lmsg = [math.cbrt(i) for i in lms]
        oklab = (self.LMSG_TO_OKLAB @ Matrix.as_column(lmsg)).get_column()
        return OKLabColor(*oklab)

    def to_oklch(self):
        return self.to_oklab().to_oklch()

    def __str__(self):
        x, y, z = round(self.x, 4), round(self.y, 4), round(self.z, 4)

        return f'xyz({x} {y} {z})'


class OKLabColor(namedtuple('_OKLabColor', 'l a b')):
    """
    Represent a color in the OKLab color space.

    *New in 0.12.0*
    """

    OKLAB_TO_LMSG = Matrix([
        [1.,  0.3963377773761749,  0.2158037573099136],
        [1., -0.1055613458156586, -0.0638541728258133],
        [1., -0.0894841775298119, -1.2914855480194092]
    ])

    LMS_TO_XYZ = Matrix([
        [ 1.2268798758459243, -0.5578149944602171,  0.2813910456659647],
        [-0.0405757452148008,  1.1122868032803170, -0.0717110580655164],
        [-0.0763729366746601, -0.4214933324022432,  1.5869240198367816]
    ])

    def to_xyz(self):
        lmsg = (self.OKLAB_TO_LMSG @ Matrix.as_column(self)).get_column()
        lms = [i ** 3 for i in lmsg]
        xyz = (self.LMS_TO_XYZ @ Matrix.as_column(lms)).get_column()
        return XYZColor(*xyz)

    def to_oklch(self):
        return OKLCHColor(
            self.l,
            math.sqrt(self.a ** 2 + self.b ** 2),
            0 if abs(self.a) < .0002 and abs(self.b) < .0002 else (((math.atan2(self.b, self.a) * 180) / math.pi % 360) + 360) % 360
        )

    def __str__(self):
        l, c, h = round(self.l, 4), round(self.a, 4), round(self.b, 4)

        return f'oklab({l} {c} {h})'

    def to_linear_rgb(self):
        return self.to_xyz().to_linear_rgb()

    def to_rgb(self):
        return self.to_xyz().to_rgb()

class OKLCHColor(namedtuple('_OKLCHColor', 'l c h')):
    """
    Represent a color in the OKLCH color space.

    *Warning*: conversion to RGB is not bound checked yet!

    *New in 0.12.0*
    """

    def __str__(self):
        l, c, h = round(self.l, 4), round(self.c, 4), round(self.h, 2)

        return f'oklch({l} {c} {h})'

    def to_oklab(self):
        return OKLabColor(
            self.l,
            self.c * math.cos(self.h * math.pi / 180),
            self.c * math.sin(self.h * math.pi / 180)
        )

    def to_xyz(self):
        return self.to_oklab().to_xyz()

    def to_rgb(self):
        return self.to_oklab().to_rgb()

    def __sub__(self, other: OKLCHColor):
        """For testing only!"""
        return sum(abs(i - j) / k for i, j, k in zip(self, other, (1, 1, 36)))


__all__ = ('chalk', 'WebColor', "RGBColor", 'LinearRGBColor', 'XYZColor', 'OKLabColor', 'OKLCHColor')
