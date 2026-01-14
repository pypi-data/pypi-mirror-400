"""ListViewer class.

This class implements an input/output view on the color model.  It lists every
unique color (e.g. unique r/g/b value) found in the color database.  Each
color is shown by small swatch and primary color name.  Some colors have
aliases -- more than one name for the same r/g/b value.  These aliases are
displayed in the small listbox at the bottom of the screen.

Clicking on a color name or swatch selects that color and updates all other
windows.  When a color is selected in a different viewer, the color list is
scrolled to the selected color and it is highlighted.  If the selected color
is an r/g/b value without a name, no scrolling occurs.

You can turn off Update On Click if all you want to see is the alias for a
given name, without selecting the color.
"""

from tkinter import (
    BooleanVar,
    BOTH,
    BROWSE,
    Canvas,
    Checkbutton,
    END,
    Frame,
    Label,
    Listbox,
    RIGHT,
    Scrollbar,
    SUNKEN,
    Toplevel,
    W,
    Y,
)

from public import public

from pynche.colordb import BadColor, rrggbb_to_triplet, triplet_to_rrggbb


ADDTOVIEW = 'Color %List Window...'


@public
class ListViewer:
    def __init__(self, switchboard, master=None) -> None:
        self._sb = switchboard
        optiondb = switchboard.optiondb()
        self._lastbox = None
        self._dontcenter = 0
        # GUI
        root = self._root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Color List')
        root.iconname('Pynche Color List')
        root.bind('<Alt-q>', self._quit)
        root.bind('<Alt-Q>', self._quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        # Create the canvas which holds everything, and its scrollbar.
        frame = self._frame = Frame(root)
        frame.pack()
        canvas = self._canvas = Canvas(frame, width=160, height=300, borderwidth=2, relief=SUNKEN)
        self._scrollbar = Scrollbar(frame)
        self._scrollbar.pack(fill=Y, side=RIGHT)
        canvas.pack(fill=BOTH, expand=1)
        # 2026-01-05(warsaw): I'm not sure what else we could do to fix pyrefly's complaint about this.
        # type: ignore[no-matching-overload]
        canvas.configure(yscrollcommand=(self._scrollbar, 'set'))
        # type: ignore[no-matching-overload]
        self._scrollbar.configure(command=(canvas, 'yview'))
        self._populate()
        # Update on click.
        self._uoc = BooleanVar()
        self._uoc.set(optiondb.get('UPONCLICK', 1))
        self._uocbtn = Checkbutton(
            root,
            text='Update on Click',
            variable=self._uoc,
            command=self._toggleupdate,
        )
        self._uocbtn.pack(expand=1, fill=BOTH)
        # The alias list.
        self._alabel = Label(root, text='Aliases:')
        self._alabel.pack()
        self._aliases = Listbox(root, height=5, selectmode=BROWSE)
        self._aliases.pack(expand=1, fill=BOTH)

    def _populate(self) -> None:
        # Create all the buttons.
        colordb = self._sb.colordb()
        canvas = self._canvas
        row = 0
        widest = 0
        bboxes = self._bboxes = []
        for name in colordb.unique_names:
            exactcolor = triplet_to_rrggbb(colordb.find_byname(name))
            canvas.create_rectangle(5, row * 20 + 5, 20, row * 20 + 20, fill=exactcolor)
            textid = canvas.create_text(25, row * 20 + 13, text=name, anchor=W)
            x1, y1, textend, y2 = canvas.bbox(textid)
            boxid = canvas.create_rectangle(
                3,
                row * 20 + 3,
                textend + 3,
                row * 20 + 23,
                outline='',
                tags=(exactcolor, 'all'),
            )
            canvas.bind('<ButtonRelease>', self._onrelease)
            bboxes.append(boxid)
            if textend + 3 > widest:
                widest = textend + 3
            row += 1
        canvheight = (row - 1) * 20 + 25
        canvas.config(scrollregion=(0, 0, 150, canvheight))
        for box in bboxes:
            x1, y1, x2, y2 = canvas.coords(box)
            canvas.coords(box, x1, y1, widest, y2)

    def _onrelease(self, event=None) -> None:
        canvas = self._canvas
        # find the current box
        assert event is not None
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        ids = canvas.find_overlapping(x, y, x, y)
        for boxid in ids:
            if boxid in self._bboxes:
                break
        else:
            return
        tags = self._canvas.gettags(boxid)
        for t in tags:
            if t[0] == '#':
                break
        else:
            return
        red, green, blue = rrggbb_to_triplet(t)
        self._dontcenter = 1
        if self._uoc.get():
            self._sb.update_views(red, green, blue)
        else:
            self.update_yourself(red, green, blue)
            self._red, self._green, self._blue = red, green, blue

    def _toggleupdate(self, _event=None) -> None:
        if self._uoc.get():
            self._sb.update_views(self._red, self._green, self._blue)

    def _quit(self, _event=None) -> None:
        self._root.quit()

    def withdraw(self, _event=None) -> None:
        self._root.withdraw()

    def deiconify(self, _event=None) -> None:
        self._root.deiconify()

    def update_yourself(self, red, green, blue) -> None:
        canvas = self._canvas
        # Turn off the last box.
        if self._lastbox:
            canvas.itemconfigure(self._lastbox, outline='')
        # Turn on the current box.
        colortag = triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colortag, outline='black')
        self._lastbox = colortag
        # Fill the aliases.
        self._aliases.delete(0, END)
        try:
            aliases = self._sb.colordb().aliases_of(red, green, blue)[1:]
        except BadColor:
            self._aliases.insert(END, '<no matching color>')
            return
        if not aliases:
            self._aliases.insert(END, '<no aliases>')
        else:
            for name in aliases:
                self._aliases.insert(END, name)
        # Maybe scroll the canvas so that the item is visible.
        if self._dontcenter:
            self._dontcenter = 0
        else:
            ig, ig, ig, y1 = canvas.coords(colortag)
            ig, ig, ig, y2 = canvas.coords(self._bboxes[-1])
            h = int(canvas['height']) * 0.5
            canvas.yview('moveto', (y1 - h) / y2)

    def save_options(self, optiondb) -> None:
        optiondb['UPONCLICK'] = self._uoc.get()

    def colordb_changed(self, _colordb) -> None:
        self._canvas.delete('all')
        self._populate()
