"""Strip viewer and related widgets.

The classes in this file implement the StripViewer shown in the top two thirds
of the main Pynche window.  It consists of three StripWidgets which display
the variations in red, green, and blue respectively of the currently selected
r/g/b color value.

Each StripWidget shows the color variations that are reachable by varying an
axis of the currently selected color.  So for example, if the color is

  (R,G,B)=(127,163,196)

then the Red variations show colors from (0,163,196) to (255,163,196), the
Green variations show colors from (127,0,196) to (127,255,196), and the Blue
variations show colors from (127,163,0) to (127,163,255).

The selected color is always visible in all three StripWidgets, and in fact
each StripWidget highlights the selected color, and has an arrow pointing to
the selected chip, which includes the value along that particular axis.

Clicking on any chip in any StripWidget selects that color, and updates all
arrows and other windows.  By toggling on Update while dragging, Pynche will
select the color under the cursor while you drag it, but be forewarned that
this can be slow.
"""

from tkinter import (
    BooleanVar,
    BOTH,
    Button,
    Canvas,
    Checkbutton,
    E,
    Frame,
    RAISED,
    RIGHT,
    W,
    YES,
)

from public import public

from pynche.colordb import (
    ColorTriplet,
    rrggbb_to_triplet,
    triplet_to_brightness,
    triplet_to_rrggbb,
)


# Load this script into the Tcl interpreter and call it in
# StripWidget.set_color().  This is about as fast as it can be with the
# current _tkinter.c interface, which doesn't support Tcl Objects.
TCLPROC = """\
proc setcolor {canv colors} {
    set i 1
    foreach c $colors {
        $canv itemconfigure $i -fill $c -outline $c
        incr i
    }
}
"""

# Tcl event types
BTNDOWN = 4
BTNUP = 5
BTNDRAG = 6

SPACE = ' '


def constant(numchips) -> list[int]:
    step = 255.0 / (numchips - 1)
    start = 0.0
    seq: list[int] = []
    while numchips > 0:
        seq.append(int(start))
        start = start + step
        numchips -= 1
    return seq


# red variations, green+blue = cyan constant
def constant_red_generator(numchips, red, _green, _blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip([red] * numchips, seq, seq))


# green variations, red+blue = magenta constant
def constant_green_generator(numchips, _red, green, _blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip(seq, [green] * numchips, seq))


# blue variations, red+green = yellow constant
def constant_blue_generator(numchips, _red, _green, blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip(seq, seq, [blue] * numchips))


# red variations, green+blue = cyan constant
def constant_cyan_generator(numchips, _red, green, blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip(seq, [green] * numchips, [blue] * numchips))


# green variations, red+blue = magenta constant
def constant_magenta_generator(numchips, red, _green, blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip([red] * numchips, seq, [blue] * numchips))


# blue variations, red+green = yellow constant
def constant_yellow_generator(numchips, red, green, _blue) -> list[ColorTriplet]:
    seq = constant(numchips)
    return list(zip([red] * numchips, [green] * numchips, seq))


class LeftArrow:
    _ARROWWIDTH = 30
    _ARROWHEIGHT = 15
    _YOFFSET = 13
    _TEXTYOFFSET = 1
    _TAG: tuple[str] = ('leftarrow',)

    def __init__(self, canvas, x) -> None:
        self._canvas = canvas
        self._arrow, self._text = self._create(x)
        self.move_to(x)

    def _create(self, x):
        arrow = self._canvas.create_line(
            x,
            self._ARROWHEIGHT + self._YOFFSET,
            x,
            self._YOFFSET,
            x + self._ARROWWIDTH,
            self._YOFFSET,
            arrow='first',
            width=3.0,
            tags=self._TAG,
        )
        text = self._canvas.create_text(
            x + self._ARROWWIDTH + 13,
            self._ARROWHEIGHT - self._TEXTYOFFSET,
            tags=self._TAG,
            text='128',
        )
        return arrow, text

    def _x(self):
        coords = list(self._canvas.coords(self._TAG))
        assert coords
        return coords[0]

    def move_to(self, x) -> None:
        deltax = x - self._x()
        self._canvas.move(self._TAG, deltax, 0)

    def set_text(self, text) -> None:
        self._canvas.itemconfigure(self._text, text=text)


class RightArrow(LeftArrow):
    _TAG = ('rightarrow',)

    def _create(self, x):
        arrow = self._canvas.create_line(
            x,
            self._YOFFSET,
            x + self._ARROWWIDTH,
            self._YOFFSET,
            x + self._ARROWWIDTH,
            self._ARROWHEIGHT + self._YOFFSET,
            arrow='last',
            width=3.0,
            tags=self._TAG,
        )
        text = self._canvas.create_text(
            x - self._ARROWWIDTH + 15,  # BAW: kludge
            self._ARROWHEIGHT - self._TEXTYOFFSET,
            justify=RIGHT,
            text='128',
            tags=self._TAG,
        )
        return arrow, text

    def _x(self):
        coords = list(self._canvas.coords(self._TAG))
        assert coords
        return coords[0] + self._ARROWWIDTH


class StripWidget:
    _CHIPHEIGHT = 50
    _CHIPWIDTH = 10
    _NUMCHIPS = 40

    def __init__(
        self,
        switchboard,
        master=None,
        chipwidth=_CHIPWIDTH,
        chipheight=_CHIPHEIGHT,
        numchips=_NUMCHIPS,
        generator=None,
        axis=None,
        label='',
        uwdvar=None,
        hexvar=None,
    ) -> None:
        self._generator = generator
        assert axis in (0, 1, 2)
        self._axis: int = axis
        self._numchips = numchips
        self._uwd = uwdvar
        self._hexp = hexvar
        self._lastchip = None
        self._sb = switchboard

        canvaswidth = numchips * (chipwidth + 1)
        canvasheight = chipheight + 43  # BAW: Kludge

        # create the canvas and pack it
        canvas = self._canvas = Canvas(
            master,
            width=canvaswidth,
            height=canvasheight,
            # borderwidth=2,
            # relief=GROOVE
        )

        canvas.pack()
        canvas.bind('<ButtonPress-1>', self._select_chip)
        canvas.bind('<ButtonRelease-1>', self._select_chip)
        canvas.bind('<B1-Motion>', self._select_chip)

        # Load a proc into the Tcl interpreter.  This is used in the
        # set_color() method to speed up setting the chip colors.
        canvas.tk.eval(TCLPROC)

        # Create the color strip.
        chips = self._chips = []
        x = 1
        y = 30
        tags = ('chip',)
        for c in range(self._numchips):
            color = 'grey'
            canvas.create_rectangle(
                x,
                y,
                x + chipwidth,
                y + chipheight,
                fill=color,
                outline=color,
                tags=tags,
            )
            x = x + chipwidth + 1  # for outline
            chips.append(color)

        # Create the strip label.
        self._label = canvas.create_text(3, y + chipheight + 8, text=label, anchor=W)

        # Create the arrow and text item.
        chipx = self._arrow_x(0)
        self._leftarrow = LeftArrow(canvas, chipx)

        chipx = self._arrow_x(len(chips) - 1)
        self._rightarrow = RightArrow(canvas, chipx)

    def _arrow_x(self, chipnum):
        coords = self._canvas.coords(chipnum + 1)
        assert coords
        x0, y0, x1, y1 = coords
        return (x1 + x0) / 2.0

    # Invoked when one of the chips is clicked.  This should just tell the
    # switchboard to set the color on all the output components.
    def _select_chip(self, event=None) -> None:
        assert event is not None
        x = event.x
        y = event.y
        canvas = self._canvas
        chip = canvas.find_overlapping(x, y, x, y)
        if chip and (1 <= chip[0] <= self._numchips):
            color = self._chips[chip[0] - 1]
            red, green, blue = rrggbb_to_triplet(color)
            etype = int(event.type)
            if etype == BTNUP or self._uwd.get():  # type: ignore[missing-attribute]
                # Update everyone.
                self._sb.update_views(red, green, blue)
            else:
                # Just track the arrows.
                self._trackarrow(chip[0], red, green, blue)

    def _trackarrow(self, chip, red, green, blue) -> None:
        # Invert the last chip.
        if self._lastchip is not None:
            color = self._canvas.itemcget(self._lastchip, 'fill')
            self._canvas.itemconfigure(self._lastchip, outline=color)
        self._lastchip = chip
        # Get the arrow's text.
        coloraxis = (red, green, blue)[self._axis]
        assert self._hexp is not None
        if self._hexp.get():
            text = hex(coloraxis)
        else:
            text = repr(coloraxis)
        # Move the arrow, and set its text.
        if coloraxis <= 128:
            # Use the left arrow.
            self._leftarrow.set_text(text)
            self._leftarrow.move_to(self._arrow_x(chip - 1))
            self._rightarrow.move_to(-100)
        else:
            # Use the right arrow.
            self._rightarrow.set_text(text)
            self._rightarrow.move_to(self._arrow_x(chip - 1))
            self._leftarrow.move_to(-100)
        # And set the chip's outline.
        brightness = triplet_to_brightness(red, green, blue)
        if brightness <= 128:
            outline = 'white'
        else:
            outline = 'black'
        self._canvas.itemconfigure(chip, outline=outline)

    def update_yourself(self, red, green, blue) -> None:
        assert self._generator
        i = 1
        chip = 0
        chips = self._chips = []
        tk = self._canvas.tk
        # Get the red, green, and blue components for all chips.
        for t in self._generator(self._numchips, red, green, blue):
            rrggbb = triplet_to_rrggbb(t)
            chips.append(rrggbb)
            tred, tgreen, tblue = t
            if tred <= red and tgreen <= green and tblue <= blue:
                chip = i
            i += 1
        # Call the raw tcl script.
        colors = SPACE.join(chips)
        tk.eval('setcolor %s {%s}' % (self._canvas._w, colors))  # type: ignore[missing-attribute]
        # Move the arrows around.
        self._trackarrow(chip, red, green, blue)

    def set(self, label, generator) -> None:
        self._canvas.itemconfigure(self._label, text=label)
        self._generator = generator


@public
class StripViewer:
    def __init__(self, switchboard, master=None) -> None:
        self._sb = switchboard
        optiondb = switchboard.optiondb()
        # Create a frame inside the master.
        frame = Frame(master, relief=RAISED, borderwidth=1)
        frame.grid(row=1, column=0, columnspan=2, sticky='NSEW')
        # Create the options to be used later.
        uwd = self._uwdvar = BooleanVar()
        uwd.set(optiondb.get('UPWHILEDRAG', 0))
        hexp = self._hexpvar = BooleanVar()
        hexp.set(optiondb.get('HEXSTRIP', 0))
        # Create the red, green, blue strips inside their own frame.
        frame1 = Frame(frame)
        frame1.pack(expand=YES, fill=BOTH)
        self._reds = StripWidget(
            switchboard,
            frame1,
            generator=constant_cyan_generator,
            axis=0,
            label='Red Variations',
            uwdvar=uwd,
            hexvar=hexp,
        )
        self._greens = StripWidget(
            switchboard,
            frame1,
            generator=constant_magenta_generator,
            axis=1,
            label='Green Variations',
            uwdvar=uwd,
            hexvar=hexp,
        )
        self._blues = StripWidget(
            switchboard,
            frame1,
            generator=constant_yellow_generator,
            axis=2,
            label='Blue Variations',
            uwdvar=uwd,
            hexvar=hexp,
        )

        # Create a frame to contain the controls.
        frame2 = Frame(frame)
        frame2.pack(expand=YES, fill=BOTH)
        frame2.columnconfigure(0, weight=20)
        frame2.columnconfigure(2, weight=20)

        padx = 8

        # Create the black button.
        blackbtn = Button(frame2, text='Black', command=self._toblack)
        blackbtn.grid(row=0, column=0, rowspan=2, sticky=W, padx=padx)

        # Create the controls.
        uwdbtn = Checkbutton(frame2, text='Update while dragging', variable=uwd)
        uwdbtn.grid(row=0, column=1, sticky=W)
        hexbtn = Checkbutton(frame2, text='Hexadecimal', variable=hexp, command=self._togglehex)
        hexbtn.grid(row=1, column=1, sticky=W)

        # Create the white button.
        whitebtn = Button(frame2, text='White', command=self._towhite)
        whitebtn.grid(row=0, column=2, rowspan=2, sticky=E, padx=padx)

    def update_yourself(self, red, green, blue) -> None:
        self._reds.update_yourself(red, green, blue)
        self._greens.update_yourself(red, green, blue)
        self._blues.update_yourself(red, green, blue)

    def _togglehex(self, _event=None) -> None:
        red, green, blue = self._sb.current_rgb()
        self.update_yourself(red, green, blue)

    def _toblack(self, _event=None) -> None:
        self._sb.update_views(0, 0, 0)

    def _towhite(self, _event=None) -> None:
        self._sb.update_views(255, 255, 255)

    def save_options(self, optiondb) -> None:
        optiondb['UPWHILEDRAG'] = self._uwdvar.get()
        optiondb['HEXSTRIP'] = self._hexpvar.get()
