"""Chip viewer and widget.

In the lower left corner of the main Pynche window, you will see two
ChipWidgets, one for the selected color and one for the nearest color.  The
selected color is the actual RGB value expressed as an X11 #COLOR name. The
nearest color is the named color from the X11 database that is closest to the
selected color in 3D space.  There may be other colors equally close, but the
nearest one is the first one found.

Clicking on the nearest color chip selects that named color.

The ChipViewer class includes the entire lower left quandrant; i.e. both the
selected and nearest ChipWidgets.
"""

from tkinter import (
    CENTER,
    DISABLED,
    Entry,
    FLAT,
    Frame,
    Label,
    RAISED,
    StringVar,
    SUNKEN,
)

from public import public

from pynche.colordb import ColorTriplet, rrggbb_to_triplet, triplet_to_rrggbb


WIDTH = 150
HEIGHT = 80


class ChipWidget:
    def __init__(
        self,
        master=None,
        width=WIDTH,
        height=HEIGHT,
        text='Color',
        initial_color='blue',
        presscmd=None,
        releasecmd=None,
    ) -> None:
        # Create the text label.
        self._label = Label(master, text=text)
        self._label.grid(row=0, column=0)
        # Create the color chip, implemented as a frame.
        self._chip = Frame(
            master,
            relief=RAISED,
            borderwidth=2,
            width=width,
            height=height,
            background=initial_color,
        )
        self._chip.grid(row=1, column=0)
        # Create the color name.
        self._namevar = StringVar()
        self._namevar.set(initial_color)
        name = Entry(
            master,
            textvariable=self._namevar,
            relief=FLAT,
            justify=CENTER,
            state=DISABLED,
            font=self._label['font'],
        )
        name.grid(row=2, column=0)
        # Create the message area.
        self._msgvar = StringVar()
        name = Entry(
            master,
            textvariable=self._msgvar,
            relief=FLAT,
            justify=CENTER,
            state=DISABLED,
            font=self._label['font'],
        )
        name.grid(row=3, column=0)
        # Set bindings.
        if presscmd:
            self._chip.bind('<ButtonPress-1>', presscmd)
        if releasecmd:
            self._chip.bind('<ButtonRelease-1>', releasecmd)

    @property
    def color(self):
        return self._chip['background']

    @color.setter
    def color(self, color) -> None:
        self._chip.config(background=color)

    def _name(self, colorname) -> None:
        self._namevar.set(colorname)

    name = property(None, _name)

    def _message(self, message) -> None:
        self._msgvar.set(message)

    message = property(None, _message)

    def press(self) -> None:
        self._chip.configure(relief=SUNKEN)

    def release(self) -> None:
        self._chip.configure(relief=RAISED)


@public
class ChipViewer:
    def __init__(self, switchboard, master=None) -> None:
        self._sb = switchboard
        self._frame = Frame(master, relief=RAISED, borderwidth=1)
        self._frame.grid(row=3, column=0, ipadx=5, sticky='NSEW')
        # Create the chip that will display the currently selected color
        # exactly.
        self._sframe = Frame(self._frame)
        self._sframe.grid(row=0, column=0)
        self._selected = ChipWidget(self._sframe, text='Selected')
        # Create the chip that will display the nearest real X11 color
        # database color name.
        self._nframe = Frame(self._frame)
        self._nframe.grid(row=0, column=1)
        self._nearest = ChipWidget(
            self._nframe,
            text='Nearest',
            presscmd=self._buttonpress,
            releasecmd=self._buttonrelease,
        )

    def update_yourself(self, red, green, blue) -> None:
        # Selected always shows the #rrggbb name of the color, nearest always
        # shows the name of the nearest color in the database.  BAW: should
        # an exact match be indicated in some way?
        #
        # Always use the #rrggbb style to actually set the color, since we may
        # not be using X color names (e.g. "web-safe" names).
        colordb = self._sb.colordb()
        rgbtuple: ColorTriplet = (red, green, blue)
        rrggbb = triplet_to_rrggbb(rgbtuple)
        # Find the nearest.
        nearest = colordb.nearest(red, green, blue)
        nearest_tuple = colordb.find_byname(nearest)
        nearest_rrggbb = triplet_to_rrggbb(nearest_tuple)
        self._selected.color = rrggbb
        self._nearest.color = nearest_rrggbb
        # Set the name and messages areas.
        self._selected.name = rrggbb
        if rrggbb == nearest_rrggbb:
            self._selected.message = nearest
        else:
            self._selected.message = ''
        self._nearest.name = nearest_rrggbb
        self._nearest.message = nearest

    def _buttonpress(self, _event=None) -> None:
        self._nearest.press()

    def _buttonrelease(self, _event=None) -> None:
        self._nearest.release()
        red, green, blue = rrggbb_to_triplet(self._nearest.color)
        self._sb.update_views(red, green, blue)
