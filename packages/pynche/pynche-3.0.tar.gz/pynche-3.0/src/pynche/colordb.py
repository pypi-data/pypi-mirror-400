"""Color Database.

This file contains one class, called ColorDB, and several utility functions.
The class must be instantiated by the get_colordb() function in this file,
passing it a filename to read a database out of.

The get_colordb() function will try to examine the file to figure out what the
format of the file is.  If it can't figure out the file format, or it has
trouble reading the file, None is returned.  You can pass get_colordb() an
optional filetype argument.

Supported file types are:

    X_RGB_TXT -- X Consortium rgb.txt format files.  Three columns of numbers
                 from 0 .. 255 separated by whitespace.  Arbitrary trailing
                 columns used as the color name.

The utility functions are useful for converting between the various expected
color formats, and for calculating other color values.
"""

import re
import sys

from contextlib import ExitStack
from typing import Pattern, TypeAlias
from importlib.resources import open_text
from math import dist

from public import public

ColorTriplet: TypeAlias = tuple[int, int, int]
public(ColorTriplet=ColorTriplet)


@public
class BadColor(Exception):
    pass


DEFAULT_DB = None
SPACE = ' '
COMMASPACE = ', '


class ColorDB:
    # Define this in the derived classes.
    _re: Pattern[str]

    def __init__(self, fp) -> None:
        self._name = fp.name
        # Maintain several dictionaries for indexing into the color database.
        # Note that while Tk supports RGB intensities of 4, 8, 12, or 16 bits,
        # for now we only support 8 bit intensities.  At least on OpenWindows,
        # all intensities in the /usr/openwin/lib/rgb.txt file are 8-bit.
        #
        # key is (red, green, blue) tuple, value is (name, [aliases])
        self._byrgb: dict[ColorTriplet, tuple[str, list[str]]] = {}
        # key is name, value is (red, green, blue)
        self._byname: dict[str, ColorTriplet] = {}
        # All unique names (non-aliases).  Populated on demand.
        self._allnames = None
        for lineno, line in enumerate(fp, start=2):
            # Get this compiled regular expression from derived class.
            if not (mo := self._re.match(line)):
                print(f'Error in {fp.name} line {lineno}', file=sys.stderr)
                continue
            # Extract the red, green, blue, and name.
            red, green, blue = self._extractrgb(mo)
            name = self._extractname(mo)
            keyname = name.lower()
            # BAW: for now the `name' is just the first named color with the
            # rgb values we find.  Later, we might want to make the two word
            # version the `name', or the CapitalizedVersion, etc.
            key = (red, green, blue)
            foundname, aliases = self._byrgb.get(key, (name, []))
            if foundname != name and foundname not in aliases:
                aliases.append(name)
            self._byrgb[key] = (foundname, aliases)
            self._byname[keyname] = key
            lineno += 1

    # Override in derived classes.
    def _extractrgb(self, mo) -> ColorTriplet:
        # Written this way for the type checker.
        # https://github.com/facebook/pyrefly/issues/2008#issuecomment-3715942320
        red, green, blue = (int(x) for x in mo.group('red', 'green', 'blue'))
        return red, green, blue

    def _extractname(self, mo):
        return mo.group('name')

    @property
    def filename(self):
        return self._name

    def find_byrgb(self, rgbtuple):
        """Return name for rgbtuple"""
        try:
            return self._byrgb[rgbtuple]
        except KeyError:
            raise BadColor(rgbtuple) from None

    def find_byname(self, name):
        """Return (red, green, blue) for name"""
        name = name.lower()
        try:
            return self._byname[name]
        except KeyError:
            raise BadColor(name) from None

    def nearest(self, red, green, blue):
        """Return the name of color nearest (red, green, blue)"""
        # BAW: should we use Voronoi diagrams, Delaunay triangulation, or
        # octree for speeding up the locating of nearest point?  Exhaustive
        # search is inefficient, but seems fast enough.
        p: ColorTriplet = red, green, blue
        distances = {name: dist(p, q) for name, q in self._byname.items()}
        # https://github.com/facebook/pyrefly/issues/2009
        # type: ignore[no-matching-overload]
        return min(distances, key=distances.get, default='')

    @property
    def unique_names(self) -> list[str]:
        if not self._allnames:
            self._allnames = sorted((name for name, aliases in self._byrgb.values()), key=str.lower)
        return self._allnames

    def aliases_of(self, red, green, blue) -> list[str]:
        try:
            name, aliases = self._byrgb[(red, green, blue)]
        except KeyError:
            raise BadColor((red, green, blue)) from None
        return [name] + aliases


class RGBColorDB(ColorDB):
    _re = re.compile(r'\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)\s+(?P<name>.*)')


class HTML40DB(ColorDB):
    _re = re.compile(r'(?P<name>\S+)\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo):
        return rrggbb_to_triplet(mo.group('hexrgb'))


class LightlinkDB(HTML40DB):
    _re = re.compile(r'(?P<name>(.+))\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractname(self, mo):
        return mo.group('name').strip()


class WebsafeDB(ColorDB):
    _re = re.compile('(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo) -> ColorTriplet:
        return rrggbb_to_triplet(mo.group('hexrgb'))

    def _extractname(self, mo):
        return mo.group('hexrgb').upper()


# The format is a tuple (RE, SCANLINES, CLASS) where RE is a compiled regular
# expression, SCANLINES is the number of header lines to scan, and CLASS is the
# class to instantiate if a match is found.
FILETYPES = [
    (re.compile('Xorg'), RGBColorDB),
    (re.compile('XConsortium'), RGBColorDB),
    (re.compile('HTML'), HTML40DB),
    (re.compile('lightlink'), LightlinkDB),
    (re.compile('Websafe'), WebsafeDB),
]


@public
def get_colordb(resource, filetype=None):
    colordb = None
    with ExitStack() as stack:
        fp = None
        if isinstance(resource, str):
            fp = stack.enter_context(open(resource, encoding='utf-8'))
        else:
            package, filename = resource
            fp = stack.enter_context(open_text(package, filename))
        line = fp.readline()
        if not line:
            return None
        # Try to determine the type of RGB file it is.
        if filetype is None:
            filetypes = FILETYPES
        else:
            filetypes = [filetype]
        for typere, class_ in filetypes:
            if typere.search(line):
                break
        else:
            return None
        # We know the type and the class to grok the type, so suck it in.
        colordb = class_(fp)
    # Save a global copy.
    global DEFAULT_DB
    DEFAULT_DB = colordb
    return colordb


_namedict = {}


@public
def rrggbb_to_triplet(color) -> ColorTriplet:
    """Converts a #rrggbb color to the tuple (red, green, blue)."""
    if (rgbtuple := _namedict.get(color)) is None:
        if color[0] != '#':
            raise BadColor(color)
        red = color[1:3]
        green = color[3:5]
        blue = color[5:7]
        rgbtuple = int(red, 16), int(green, 16), int(blue, 16)
        _namedict[color] = rgbtuple
    # https://github.com/facebook/pyrefly/issues/913
    # type: ignore[unbound-name]
    return rgbtuple


_tripdict: dict[ColorTriplet | str, str] = {}


@public
def triplet_to_rrggbb(rgbtuple: ColorTriplet) -> str:
    """Converts a (red, green, blue) tuple to #rrggbb."""
    if (hexname := _tripdict.get(rgbtuple)) is None:
        hexname = '#%02x%02x%02x' % rgbtuple
        _tripdict[rgbtuple] = hexname
    # https://github.com/facebook/pyrefly/issues/913
    # type: ignore[unbound-name]
    return hexname


@public
def triplet_to_brightness(red, green, blue):
    # Return the brightness (grey level) along the scale 0.0==black to
    # 1.0==white
    return red * 0.299 + green * 0.587 + blue * 0.114
