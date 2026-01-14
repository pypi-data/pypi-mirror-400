"""Switchboard class.

This class is used to coordinate updates among all Viewers.  Every Viewer must
conform to the following interface:

    - it must include a method called update_yourself() which takes three
      arguments; the red, green, and blue values of the selected color.

    - When a Viewer selects a color and wishes to update all other Views, it
      should call update_views() on the Switchboard object.  Note that the
      Viewer typically does *not* update itself before calling update_views(),
      since this would cause it to get updated twice.

Optionally, Viewers can also implement:

    - save_options() which takes an optiondb (a dictionary).  Store into this
      dictionary any values the Viewer wants to save in the persistent
      ~/.pynche file.  This dictionary is saved using marshal.  The namespace
      for the keys is ad-hoc; make sure you don't clobber some other Viewer's
      keys!

    - withdraw() which takes no arguments.  This is called when Pynche is
      unmapped.  All Viewers should implement this.

    - colordb_changed() which takes a single argument, an instance of
      ColorDB.  This is called whenever the color name database is changed and
      gives a chance for the Viewers to do something on those events.  See
      ListViewer for details.

External Viewers are found dynamically.  Viewer modules should have names such
as FooViewer.py.  If such a named module has a module global variable called
ADDTOVIEW and this variable is true, the Viewer will be added dynamically to
the `View' menu.  ADDTOVIEW contains a string which is used as the menu item
to display the Viewer (one kludge: if the string contains a `%', this is used
to indicate that the next character will get an underline in the menu,
otherwise the first character is underlined).

FooViewer.py should contain a class called FooViewer, and its constructor
should take two arguments, an instance of Switchboard, and optionally a Tk
master window.
"""

import sys
import marshal


class Switchboard:
    def __init__(self, initfile) -> None:
        self._initfile = initfile
        self._colordb = None
        self._optiondb = {}
        self._views = []
        self._red = 0
        self._green = 0
        self._blue = 0
        self._canceled = False
        # Read the initialization file.
        if initfile:
            try:
                with open(initfile, 'rb') as fp:
                    self._optiondb = marshal.load(fp)
                    if not isinstance(self._optiondb, dict):
                        print(
                            f'Problem reading options from file: {initfile}',
                            file=sys.stderr,
                        )
                        self._optiondb = {}
            except (OSError, EOFError, ValueError):
                pass

    def add_view(self, view):
        self._views.append(view)

    def update_views(self, red, green, blue):
        self._red = red
        self._green = green
        self._blue = blue
        for v in self._views:
            v.update_yourself(red, green, blue)

    def update_views_current(self):
        self.update_views(self._red, self._green, self._blue)

    def current_rgb(self):
        return self._red, self._green, self._blue

    def colordb(self):
        return self._colordb

    def set_colordb(self, colordb):
        self._colordb = colordb
        for v in self._views:
            if hasattr(v, 'colordb_changed'):
                v.colordb_changed(colordb)
        self.update_views_current()

    def optiondb(self):
        return self._optiondb

    def save_views(self):
        # Save the current color.
        self._optiondb['RED'] = self._red
        self._optiondb['GREEN'] = self._green
        self._optiondb['BLUE'] = self._blue
        for v in self._views:
            if hasattr(v, 'save_options'):
                v.save_options(self._optiondb)
        # Save the name of the file used for the color database.  We'll try to
        # load this first.
        assert self._colordb is not None
        self._optiondb['DBFILE'] = self._colordb.filename
        try:
            with open(self._initfile, 'wb') as fp:
                marshal.dump(self._optiondb, fp)
        except OSError:
            print(
                f'Cannot write options to file: {self._initfile}',
                file=sys.stderr,
            )

    def withdraw_views(self):
        for v in self._views:
            if hasattr(v, 'withdraw'):
                v.withdraw()

    @property
    def canceled(self):
        return self._canceled

    @canceled.setter
    def canceled(self, flag):
        self._canceled = flag
