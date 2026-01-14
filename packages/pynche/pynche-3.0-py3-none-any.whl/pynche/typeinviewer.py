"""TypeinViewer class.

The TypeinViewer is what you see at the lower right of the main Pynche
widget.  It contains three text entry fields, one each for red, green, blue.
Input into these windows is highly constrained; it only allows you to enter
values that are legal for a color axis.  This usually means 0-255 for decimal
input and 0x0 - 0xff for hex input.

You can toggle whether you want to view and input the values in either decimal
or hex by clicking on Hexadecimal.  By clicking on Update while typing, the
color selection will be made on every change to the text field.  Otherwise,
you must hit Return or Tab to select the color.
"""

from tkinter import (
    BooleanVar,
    Checkbutton,
    E,
    END,
    Entry,
    Frame,
    INSERT,
    Label,
    RAISED,
    W,
)

from public import public


@public
class TypeinViewer:
    def __init__(self, switchboard, master=None) -> None:
        # Non-GUI variables.
        self._sb = switchboard
        optiondb = switchboard.optiondb()
        self._hexp = BooleanVar()
        self._hexp.set(optiondb.get('HEXTYPE', 0))
        self._uwtyping = BooleanVar()
        self._uwtyping.set(optiondb.get('UPWHILETYPE', 0))
        # Create the GUI.
        self._frame = Frame(master, relief=RAISED, borderwidth=1)
        self._frame.grid(row=3, column=1, sticky='NSEW')
        # Red.
        self._xl = Label(self._frame, text='Red:')
        self._xl.grid(row=0, column=0, sticky=E)
        subframe = Frame(self._frame)
        subframe.grid(row=0, column=1)
        self._xox = Label(subframe, text='0x')
        self._xox.grid(row=0, column=0, sticky=E)
        self._xox['font'] = 'courier'
        self._x = Entry(subframe, width=3)
        self._x.grid(row=0, column=1)
        self._x.bindtags(self._x.bindtags() + ('Normalize', 'Update'))
        self._x.bind_class('Normalize', '<Key>', self._normalize)
        self._x.bind_class('Update', '<Key>', self._maybeupdate)
        # Green.
        self._yl = Label(self._frame, text='Green:')
        self._yl.grid(row=1, column=0, sticky=E)
        subframe = Frame(self._frame)
        subframe.grid(row=1, column=1)
        self._yox = Label(subframe, text='0x')
        self._yox.grid(row=0, column=0, sticky=E)
        self._yox['font'] = 'courier'
        self._y = Entry(subframe, width=3)
        self._y.grid(row=0, column=1)
        self._y.bindtags(self._y.bindtags() + ('Normalize', 'Update'))
        # Blue.
        self._zl = Label(self._frame, text='Blue:')
        self._zl.grid(row=2, column=0, sticky=E)
        subframe = Frame(self._frame)
        subframe.grid(row=2, column=1)
        self._zox = Label(subframe, text='0x')
        self._zox.grid(row=0, column=0, sticky=E)
        self._zox['font'] = 'courier'
        self._z = Entry(subframe, width=3)
        self._z.grid(row=0, column=1)
        self._z.bindtags(self._z.bindtags() + ('Normalize', 'Update'))
        # Update while typing?
        self._uwt = Checkbutton(self._frame, text='Update while typing', variable=self._uwtyping)
        self._uwt.grid(row=3, column=0, columnspan=2, sticky=W)
        # Hex/Dec
        self._hex = Checkbutton(
            self._frame,
            text='Hexadecimal',
            variable=self._hexp,
            command=self._togglehex,
        )
        self._hex.grid(row=4, column=0, columnspan=2, sticky=W)

    def _togglehex(self, _event=None) -> None:
        red, green, blue = self._sb.current_rgb()
        if self._hexp.get():
            label = '0x'
        else:
            label = '  '
        self._xox['text'] = label
        self._yox['text'] = label
        self._zox['text'] = label
        self.update_yourself(red, green, blue)

    def _normalize(self, event=None) -> None:
        assert event is not None
        ew = event.widget
        contents = ew.get()
        icursor = ew.index(INSERT)
        if contents and contents[0] in 'xX' and self._hexp.get():
            contents = '0' + contents
        # Figure out the contents in the current base.
        try:
            if self._hexp.get():
                v = int(contents, 16)
            else:
                v = int(contents)
        except ValueError:
            v = None
        # If value is not legal, or empty, delete the last character inserted
        # and ring the bell.  Don't ring the bell if the field is empty (it'll
        # just equal zero.
        if v is None:
            pass
        elif v < 0 or v > 255:
            i = ew.index(INSERT)
            if event.char:
                contents = contents[: i - 1] + contents[i:]
                icursor -= 1
            ew.bell()
        elif self._hexp.get():
            contents = hex(v)[2:]
        else:
            contents = int(v)
        ew.delete(0, END)
        ew.insert(0, contents)
        ew.icursor(icursor)

    def _maybeupdate(self, event=None) -> None:
        assert event is not None
        if self._uwtyping.get() or event.keysym in ('Return', 'Tab'):
            self._update(event)

    def _update(self, _event=None) -> None:
        redstr = self._x.get() or '0'
        greenstr = self._y.get() or '0'
        bluestr = self._z.get() or '0'
        if self._hexp.get():
            base = 16
        else:
            base = 10
        red, green, blue = [int(x, base) for x in (redstr, greenstr, bluestr)]
        self._sb.update_views(red, green, blue)

    def update_yourself(self, red, green, blue) -> None:
        if self._hexp.get():
            sred, sgreen, sblue = [hex(x)[2:] for x in (red, green, blue)]
        else:
            sred, sgreen, sblue = red, green, blue
        x, y, z = self._x, self._y, self._z
        xicursor = x.index(INSERT)
        yicursor = y.index(INSERT)
        zicursor = z.index(INSERT)
        x.delete(0, END)
        y.delete(0, END)
        z.delete(0, END)
        x.insert(0, sred)
        y.insert(0, sgreen)
        z.insert(0, sblue)
        x.icursor(xicursor)
        y.icursor(yicursor)
        z.icursor(zicursor)

    def save_options(self, optiondb) -> None:
        optiondb['HEXTYPE'] = self._hexp.get()
        optiondb['UPWHILETYPE'] = self._uwtyping.get()
