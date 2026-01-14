"""Main Pynche (Pythonically Natural Color and Hue Editor) widget.

This window provides the basic decorations, primarily including the menubar.
It is used to bring up other windows.
"""

import os
import tkinter
import functools
import webbrowser

from importlib import import_module
from importlib.resources import files
from tkinter import (
    Button,
    filedialog,
    Frame,
    LEFT,
    Menu,
    messagebox,
    RAISED,
    Tk,
    Toplevel,
)
from typing import Any

from pynche.colordb import get_colordb


# Milliseconds between interrupt checks
KEEPALIVE_TIMER = 500

HELP_FILE = 'https://gitlab.com/warsaw/pynche/-/blob/main/README.md'


class PyncheWidget:
    def __init__(self, version, switchboard, master=None) -> None:
        self._sb = switchboard
        self._version = version
        self._textwin = None
        self._listwin = None
        self._detailswin = None
        self._dialogstate = {}
        modal = self._modal = not not master
        # If a master was given, we are running as a modal dialog servant to
        # some other application.  We rearrange our UI in this case (there's
        # no File menu and we get `Okay' and `Cancel' buttons), and we do a
        # grab_set() to make ourselves modal
        tkroot: Toplevel | Tk | Any
        if modal:
            tkroot = Toplevel(master, class_='Pynche')
            tkroot.grab_set()
            tkroot.withdraw()
        else:
            # Is there already a default root for Tk, say because we're
            # running under Guido's IDE? :-) Two conditions say no, either the
            # _default_root is None or it is unset.
            tkroot = getattr(tkinter, '_default_root', None)
            if not tkroot:
                tkroot = Tk(className='Pynche')
            # But this isn't our top level widget, so make it invisible.
            tkroot.withdraw()
        self._tkroot = tkroot
        # Create the menubar.
        menubar = self._menubar = Menu(tkroot)
        # File menu.
        filemenu = self._filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Load palette...', command=self._load, underline=0)
        if not modal:
            filemenu.add_command(
                label='Quit',
                command=self._quit,
                accelerator='Alt-Q',
                underline=0,
            )
        # View menu.
        views = make_view_popups(self._sb, self._tkroot)
        viewmenu = Menu(menubar, tearoff=0)
        for v in views:
            viewmenu.add_command(label=v.menutext(), command=v.popup, underline=v.underline())
        # Help menu.
        helpmenu = Menu(menubar, name='help', tearoff=0)
        helpmenu.add_command(label='About Pynche...', command=self._popup_about, underline=0)
        helpmenu.add_command(label='Help...', command=self._popup_usage, underline=0)
        # Tie them all together.
        menubar.add_cascade(label='File', menu=filemenu, underline=0)
        menubar.add_cascade(label='View', menu=viewmenu, underline=0)
        menubar.add_cascade(label='Help', menu=helpmenu, underline=0)
        # Now create the top level window.
        root = self._root = Toplevel(tkroot, class_='Pynche', menu=menubar)
        root.protocol('WM_DELETE_WINDOW', modal and self._bell or self._quit)
        root.title('Pynche %s' % version)
        root.iconname('Pynche')
        # Only bind accelerators for the File->Quit menu item if running as a
        # standalone app.
        if not modal:
            root.bind('<Alt-q>', self._quit)
            root.bind('<Alt-Q>', self._quit)
        else:
            # We're a modal dialog so we have a new row of buttons.
            bframe = Frame(root, borderwidth=1, relief=RAISED)
            bframe.grid(row=4, column=0, columnspan=2, sticky='EW', ipady=5)
            okay = Button(bframe, text='Okay', command=self._okay)
            okay.pack(side=LEFT, expand=1)
            cancel = Button(bframe, text='Cancel', command=self._cancel)
            cancel.pack(side=LEFT, expand=1)

    def _quit(self, _event=None) -> None:
        self._tkroot.quit()

    def _bell(self, _event=None) -> None:
        self._tkroot.bell()

    def _okay(self, _event=None) -> None:
        self._sb.withdraw_views()
        self._tkroot.grab_release()
        self._quit()

    def _cancel(self, _event=None) -> None:
        self._sb.canceled = True
        self._okay()

    def _keepalive(self) -> None:
        # Exercise the Python interpreter regularly so keyboard interrupts get
        # through.
        self._tkroot.tk.createtimerhandler(KEEPALIVE_TIMER, self._keepalive)

    def start(self) -> None:
        if not self._modal:
            self._keepalive()
        self._tkroot.mainloop()

    @property
    def window(self):
        return self._root

    def _popup_about(self, _event=None) -> None:
        from Main import __version__  # type: ignore[missing-import]

        messagebox.showinfo(
            'About Pynche ' + __version__,
            """\
Pynche %s
The PYthonically Natural
Color and Hue Editor

For information
contact: Barry Warsaw
email:   barry@python.org
web:     https://gitlab.com/warsaw/pynche"""
            % __version__,
        )

    def _popup_usage(self, _event=None) -> None:
        webbrowser.open(HELP_FILE, new=2)

    def _load(self, _event=None) -> None:
        while True:
            idir, ifile = os.path.split(self._sb.colordb().filename)
            filename = filedialog.askopenfilename(
                filetypes=[
                    ('Text files', '*.txt'),
                    ('All files', '*'),
                ],
                initialdir=idir,
                initialfile=ifile,
            )
            if not filename:
                # Cancel button.
                return
            try:
                colordb = get_colordb(filename)
            except OSError:
                messagebox.showerror(
                    'Read error',
                    f"""\
Could not open file for reading:
{filename}""",
                )
                continue
            if colordb is None:
                messagebox.showerror(
                    'Unrecognized color file type',
                    f"""\
Unrecognized color file type in file:
{filename}""",
                )
                continue
            break
        self._sb.set_colordb(colordb)

    def withdraw(self) -> None:
        self._root.withdraw()

    def deiconify(self) -> None:
        self._root.deiconify()


@functools.total_ordering
class PopupViewer:
    def __init__(self, module, name, switchboard, root) -> None:
        self._m = module
        self._name = name
        self._sb = switchboard
        self._root = root
        self._menutext = module.ADDTOVIEW
        # Find the underline character.
        underline = module.ADDTOVIEW.find('%')
        if underline == -1:
            underline = 0
        else:
            self._menutext = module.ADDTOVIEW.replace('%', '', 1)
        self._underline = underline
        self._window = None

    def menutext(self):
        return self._menutext

    def underline(self):
        return self._underline

    def popup(self, _event=None) -> None:
        if not self._window:
            # class and module must have the same name
            class_ = getattr(self._m, self._name)
            self._window = class_(self._sb, self._root)
            self._sb.add_view(self._window)
        self._window.deiconify()

    def __eq__(self, other):
        if isinstance(self, PopupViewer):
            return self._menutext == other._menutext
        return NotImplemented

    def __lt__(self, other):
        if isinstance(self, PopupViewer):
            return self._menutext < other._menutext
        return NotImplemented


def make_view_popups(switchboard, root):
    viewers = []
    # First, load our own viewers.
    for traversable in files('pynche').iterdir():
        # https://github.com/facebook/pyrefly/issues/2010
        # type: ignore[missing-attribute]
        basename = traversable.stem
        if basename.endswith('viewer'):
            module = import_module(f'pynche.{basename}')
            if hasattr(module, 'ADDTOVIEW') and module.ADDTOVIEW:
                # This is an external viewer; find the class.
                for clsname in module.__all__:
                    if clsname.endswith('Viewer'):
                        v = PopupViewer(module, clsname, switchboard, root)
                        viewers.append(v)
    # Sort alphabetically.
    return sorted(viewers)
