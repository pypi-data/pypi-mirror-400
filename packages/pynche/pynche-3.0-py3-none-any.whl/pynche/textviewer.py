"""TextViewer class.

The TextViewer allows you to see how the selected color would affect various
characteristics of a Tk text widget.  This is an output viewer only.

In the top part of the window is a standard text widget with some sample text
in it.  You are free to edit this text in any way you want (BAW: allow you to
change font characteristics).  If you want changes in other viewers to update
text characteristics, turn on Track color changes.

To select which characteristic tracks the change, select one of the radio
buttons in the window below.  Text foreground and background affect the text
in the window above.  The Selection is what you see when you click the middle
button and drag it through some text.  The Insertion is the insertion cursor
in the text window (which only has a background).
"""

from tkinter import (
    BooleanVar,
    Checkbutton,
    DISABLED,
    E,
    END,
    Frame,
    GROOVE,
    INSERT,
    IntVar,
    Label,
    NORMAL,
    Radiobutton,
    SEL,
    SUNKEN,
    Text,
    Toplevel,
    X,
    YES,
)

from public import public

from pynche.colordb import BadColor, rrggbb_to_triplet, triplet_to_rrggbb


ADDTOVIEW = 'Text Window...'


@public
class TextViewer:
    def __init__(self, switchboard, master=None) -> None:
        self._sb = switchboard
        optiondb = switchboard.optiondb()
        root = self._root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Text Window')
        root.iconname('Pynche Text Window')
        root.bind('<Alt-q>', self._quit)
        root.bind('<Alt-Q>', self._quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        self._text = Text(
            root,
            relief=SUNKEN,
            background=optiondb.get('TEXTBG', 'black'),
            foreground=optiondb.get('TEXTFG', 'white'),
            width=35,
            height=15,
        )
        sfg = optiondb.get('TEXT_SFG')
        if sfg:
            self._text.configure(selectforeground=sfg)
        sbg = optiondb.get('TEXT_SBG')
        if sbg:
            self._text.configure(selectbackground=sbg)
        ibg = optiondb.get('TEXT_IBG')
        if ibg:
            self._text.configure(insertbackground=ibg)
        self._text.pack()
        self._text.insert(
            0.0,
            optiondb.get(
                'TEXT',
                """\
Insert some stuff here and play
with the buttons below to see
how the colors interact in
textual displays.

See how the selection can also
be affected by tickling the buttons
and choosing a color.""",
            ),
        )
        insert = optiondb.get('TEXTINS')
        if insert:
            self._text.mark_set(INSERT, insert)
        try:
            start, end = optiondb.get('TEXTSEL', (6.0, END))
            self._text.tag_add(SEL, start, end)
        except ValueError:
            # Selection wasn't set.
            pass
        self._text.focus_set()
        self._trackp = BooleanVar()
        self._trackp.set(optiondb.get('TRACKP', 0))
        self._which = IntVar()
        self._which.set(optiondb.get('WHICH', 0))
        #
        # track toggle
        self._t = Checkbutton(
            root,
            text='Track color changes',
            variable=self._trackp,
            relief=GROOVE,
            command=self._toggletrack,
        )
        self._t.pack(fill=X, expand=YES)
        frame = self._frame = Frame(root)
        frame.pack()
        # Labels.
        self._labels = []
        row = 2
        for text in ('Text:', 'Selection:', 'Insertion:'):
            label = Label(frame, text=text)
            label.grid(row=row, column=0, sticky=E)
            self._labels.append(label)
            row += 1
        col = 1
        for text in ('Foreground', 'Background'):
            label = Label(frame, text=text)
            label.grid(row=1, column=col)
            self._labels.append(label)
            col += 1
        self._radios = []
        for col in (1, 2):
            for row in (2, 3, 4):
                # There is no insertforeground option.
                if row == 4 and col == 1:
                    continue
                r = Radiobutton(
                    frame,
                    variable=self._which,
                    value=(row - 2) * 2 + col - 1,
                    command=self._set_color,
                )
                r.grid(row=row, column=col)
                self._radios.append(r)
        self._toggletrack()

    def _quit(self, _event=None) -> None:
        self._root.quit()

    def withdraw(self, _event=None) -> None:
        self._root.withdraw()

    def deiconify(self, _event=None) -> None:
        self._root.deiconify()

    def _forceupdate(self, _event=None) -> None:
        self._sb.update_views_current()

    def _toggletrack(self, _event=None) -> None:
        if self._trackp.get():
            state = NORMAL
            fg = self._radios[0]['foreground']
        else:
            state = DISABLED
            fg = self._radios[0]['disabledforeground']
        for r in self._radios:
            r.configure(state=state)
        for label in self._labels:
            label.configure(foreground=fg)

    def _set_color(self, _event=None) -> None:
        which = self._which.get()
        text = self._text
        match which := self._which.get():
            case 0:
                color = text['foreground']
            case 1:
                color = text['background']
            case 2:
                color = text['selectforeground']
            case 3:
                color = text['selectbackground']
            case 5:
                color = text['insertbackground']
            case _:
                raise AssertionError(f'Unexpected WHICH option: {which}')
        try:
            red, green, blue = rrggbb_to_triplet(color)
        except BadColor:
            # It must have been a color name.
            red, green, blue = self._sb.colordb().find_byname(color)
        self._sb.update_views(red, green, blue)

    def update_yourself(self, red, green, blue) -> None:
        if self._trackp.get():
            colorname = triplet_to_rrggbb((red, green, blue))
            which = self._which.get()
            text = self._text
            if which == 0:
                text.configure(foreground=colorname)
            elif which == 1:
                text.configure(background=colorname)
            elif which == 2:
                text.configure(selectforeground=colorname)
            elif which == 3:
                text.configure(selectbackground=colorname)
            elif which == 5:
                text.configure(insertbackground=colorname)

    def save_options(self, optiondb) -> None:
        optiondb['TRACKP'] = self._trackp.get()
        optiondb['WHICH'] = self._which.get()
        optiondb['TEXT'] = self._text.get(0.0, 'end - 1c')
        optiondb['TEXTSEL'] = self._text.tag_ranges(SEL)[0:2]
        optiondb['TEXTINS'] = self._text.index(INSERT)
        optiondb['TEXTFG'] = self._text['foreground']
        optiondb['TEXTBG'] = self._text['background']
        optiondb['TEXT_SFG'] = self._text['selectforeground']
        optiondb['TEXT_SBG'] = self._text['selectbackground']
        optiondb['TEXT_IBG'] = self._text['insertbackground']
