"""DetailsViewer class.

This class implements a pure input window which allows you to meticulously
edit the current color.  You have both mouse control of the color (via the
buttons along the bottom row), and there are keyboard bindings for each of the
increment/decrement buttons.

The top three check buttons allow you to specify which of the three color
variations are tied together when incrementing and decrementing.  Red, green,
and blue are self evident.  By tying together red and green, you can modify
the yellow level of the color.  By tying together red and blue, you can modify
the magenta level of the color.  By tying together green and blue, you can
modify the cyan level, and by tying all three together, you can modify the
grey level.

The behavior at the boundaries (0 and 255) are defined by the `At boundary'
option menu:

    Stop
        When the increment or decrement would send any of the tied variations
        out of bounds, the entire delta is discarded.

    Wrap Around
        When the increment or decrement would send any of the tied variations
        out of bounds, the out of bounds variation is wrapped around to the
        other side.  Thus if red were at 238 and 25 were added to it, red
        would have the value 7.

    Preserve Distance
        When the increment or decrement would send any of the tied variations
        out of bounds, all tied variations are wrapped as one, so as to
        preserve the distance between them.  Thus if green and blue were tied,
        and green was at 238 while blue was at 223, and an increment of 25
        were applied, green would be at 15 and blue would be at 0.

    Squash
        When the increment or decrement would send any of the tied variations
        out of bounds, the out of bounds variation is set to the ceiling of
        255 or floor of 0, as appropriate.  In this way, all tied variations
        are squashed to one edge or the other.

The following key bindings can be used as accelerators.  Note that Pynche can
fall behind if you hold the key down as a key repeat:

Left arrow == -1
Right arrow == +1

Control + Left == -10
Control + Right == 10

Shift + Left == -25
Shift + Right == +25
"""

from enum import Enum
from tkinter import (
    Button,
    Checkbutton,
    E,
    Frame,
    IntVar,
    Label,
    LEFT,
    OptionMenu,
    StringVar,
    Toplevel,
    W,
    X,
    YES,
)

from public import public


class BoundaryBehavior(Enum):
    STOP = 'Stop'
    WRAP = 'Wrap Around'
    RATIO = 'Preserve Distance'
    GRAVITY = 'Squash'


class Direction(Enum):
    Left = -1
    Center = 0
    Right = 1


ADDTOVIEW = 'Details Window...'


@public
class DetailsViewer:
    def __init__(self, switchboard, master=None) -> None:
        self._sb = switchboard
        optiondb = switchboard.optiondb()
        self._red, self._green, self._blue = switchboard.current_rgb()
        # GUI
        root = self._root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Details Window')
        root.iconname('Pynche Details Window')
        root.bind('<Alt-q>', self._quit)
        root.bind('<Alt-Q>', self._quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        # Key bindings.
        root.bind('<KeyPress-Left>', self._minus1)
        root.bind('<KeyPress-Right>', self._plus1)
        root.bind('<Control-KeyPress-Left>', self._minus10)
        root.bind('<Control-KeyPress-Right>', self._plus10)
        root.bind('<Shift-KeyPress-Left>', self._minus25)
        root.bind('<Shift-KeyPress-Right>', self._plus25)
        # Color ties.
        frame = self._frame = Frame(root)
        frame.pack(expand=YES, fill=X)
        self._l1 = Label(frame, text='Move Sliders:')
        self._l1.grid(row=1, column=0, sticky=E)
        self._rvar = IntVar()
        self._rvar.set(optiondb.get('RSLIDER', 4))
        self._radio1 = Checkbutton(
            frame,
            text='Red',
            variable=self._rvar,
            command=self._effect,
            onvalue=4,
            offvalue=0,
        )
        self._radio1.grid(row=1, column=1, sticky=W)
        self._gvar = IntVar()
        self._gvar.set(optiondb.get('GSLIDER', 2))
        self._radio2 = Checkbutton(
            frame,
            text='Green',
            variable=self._gvar,
            command=self._effect,
            onvalue=2,
            offvalue=0,
        )
        self._radio2.grid(row=2, column=1, sticky=W)
        self._bvar = IntVar()
        self._bvar.set(optiondb.get('BSLIDER', 1))
        self._radio3 = Checkbutton(
            frame,
            text='Blue',
            variable=self._bvar,
            command=self._effect,
            onvalue=1,
            offvalue=0,
        )
        self._radio3.grid(row=3, column=1, sticky=W)
        self._l2 = Label(frame)
        self._l2.grid(row=4, column=1, sticky=W)
        self._effect()
        # Boundary behavior.
        self._l3 = Label(frame, text='At boundary:')
        self._l3.grid(row=5, column=0, sticky=E)
        self._boundvar = StringVar()
        self._boundvar.set(optiondb.get('ATBOUND', BoundaryBehavior.STOP.value))
        self._omenu = OptionMenu(
            frame,
            self._boundvar,
            BoundaryBehavior.STOP.value,
            BoundaryBehavior.WRAP.value,
            BoundaryBehavior.RATIO.value,
            BoundaryBehavior.GRAVITY.value,
        )
        self._omenu.grid(row=5, column=1, sticky=W)
        self._omenu.configure(width=17)
        # Buttons.
        frame = self._btnframe = Frame(frame)
        frame.grid(row=0, column=0, columnspan=2, sticky='EW')
        self._down25 = Button(frame, text='-25', command=self._minus25)
        self._down10 = Button(frame, text='-10', command=self._minus10)
        self._down1 = Button(frame, text='-1', command=self._minus1)
        self._up1 = Button(frame, text='+1', command=self._plus1)
        self._up10 = Button(frame, text='+10', command=self._plus10)
        self._up25 = Button(frame, text='+25', command=self._plus25)
        self._down25.pack(expand=YES, fill=X, side=LEFT)
        self._down10.pack(expand=YES, fill=X, side=LEFT)
        self._down1.pack(expand=YES, fill=X, side=LEFT)
        self._up1.pack(expand=YES, fill=X, side=LEFT)
        self._up10.pack(expand=YES, fill=X, side=LEFT)
        self._up25.pack(expand=YES, fill=X, side=LEFT)

    def _effect(self, event=None):
        tie = self._rvar.get() + self._gvar.get() + self._bvar.get()
        if tie in (0, 1, 2, 4):
            text = ''
        else:
            text = '(= %s Level)' % {3: 'Cyan', 5: 'Magenta', 6: 'Yellow', 7: 'Grey'}[tie]
        self._l2.configure(text=text)

    def _quit(self, event=None):
        self._root.quit()

    def withdraw(self, event=None):
        self._root.withdraw()

    def deiconify(self, event=None):
        self._root.deiconify()

    def _minus25(self, event=None):
        self._delta(-25)

    def _minus10(self, event=None):
        self._delta(-10)

    def _minus1(self, event=None):
        self._delta(-1)

    def _plus1(self, event=None):
        self._delta(1)

    def _plus10(self, event=None):
        self._delta(10)

    def _plus25(self, event=None):
        self._delta(25)

    def _delta(self, delta):
        tie = []
        if self._rvar.get():
            red = self._red + delta
            tie.append(red)
        else:
            red = self._red
        if self._gvar.get():
            green = self._green + delta
            tie.append(green)
        else:
            green = self._green
        if self._bvar.get():
            blue = self._blue + delta
            tie.append(blue)
        else:
            blue = self._blue
        # Now apply at boundary behavior.
        atbound = BoundaryBehavior(self._boundvar.get())
        if atbound is BoundaryBehavior.STOP:
            if red < 0 or green < 0 or blue < 0 or red > 255 or green > 255 or blue > 255:
                red, green, blue = self._red, self._green, self._blue
        elif atbound is BoundaryBehavior.WRAP or (
            atbound is BoundaryBehavior.RATIO and len(tie) < 2
        ):
            if red < 0:
                red += 256
            if green < 0:
                green += 256
            if blue < 0:
                blue += 256
            if red > 255:
                red -= 256
            if green > 255:
                green -= 256
            if blue > 255:
                blue -= 256
        elif atbound is BoundaryBehavior.RATIO:
            # For when 2 or 3 colors are tied together.
            direction = Direction.Center
            for c in tie:
                if c < 0:
                    direction = Direction.Left
                elif c > 255:
                    direction = Direction.Right
            if direction is Direction.Left:
                delta = max(tie)
                if self._rvar.get():
                    red = red + 255 - delta
                if self._gvar.get():
                    green = green + 255 - delta
                if self._bvar.get():
                    blue = blue + 255 - delta
            elif direction is Direction.Right:
                delta = min(tie)
                if self._rvar.get():
                    red = red - delta
                if self._gvar.get():
                    green = green - delta
                if self._bvar.get():
                    blue = blue - delta
        elif atbound == BoundaryBehavior.GRAVITY:
            if red < 0:
                red = 0
            if green < 0:
                green = 0
            if blue < 0:
                blue = 0
            if red > 255:
                red = 255
            if green > 255:
                green = 255
            if blue > 255:
                blue = 255
        self._sb.update_views(red, green, blue)
        self._root.update_idletasks()

    def update_yourself(self, red, green, blue):
        self._red = red
        self._green = green
        self._blue = blue

    def save_options(self, optiondb):
        optiondb['RSLIDER'] = self._rvar.get()
        optiondb['GSLIDER'] = self._gvar.get()
        optiondb['BSLIDER'] = self._bvar.get()
        optiondb['ATBOUND'] = self._boundvar.get()
