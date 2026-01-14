===================
 Welcome to Pynche
===================

This is the *Py*\ thonically *N*\ atural *C*\ olor and *H*\ ue *E*\ ditor.

Pynche is based largely on a similar color editor I wrote many years ago for the SunView window system.  That
editor was called ICE: the Interactive Color Editor.  I'd always wanted to port the editor to X but didn't
feel like hacking X and C code to do it.  Fast forward many years, to where Python + Tkinter provided such a
nice programming environment, with enough power, that I finally buckled down and implemented it.  I changed
the name because there were too many other systems have the acronym ``ICE``.


Requirements
============

``pynche`` requires Python 3.10 or newer.  It also requires `tkinter
<https://docs.python.org/3/library/tkinter.html>`_ which is shipped in the CPython standard library, but may
be distributed as a separate package in your operating system's package manager.  On macOS (where I test
things), you need to ``brew install python-tk``.


Documentation
=============

More information is available in the :doc:`user guide <using>`.


Project details
===============

 * Project home: https://gitlab.com/warsaw/pynche
 * Report bugs at: https://gitlab.com/warsaw/pynche/issues
 * Code hosting: https://gitlab.com/warsaw/pynche.git
 * Documentation: https://pynche.readthedocs.io
 * PyPI: https://pypi.python.org/pypi/pynche


A modern day warrior
====================

Pynche was `finally removed <https://github.com/python/cpython/issues/91551>`_ from the CPython repository in
Python 3.11, and moved into its own repo.  Given that the code in CPython wasn't even Python 3 compatible at
the time, this was long overdue.

I don't intend to support this too much, but I'll keep it working (with your help!) and it still makes a nice
demo of using `tkinter <https://docs.python.org/3/library/tkinter.html>`_ from Python, so I guess here ya go.
Contributions and collaborators welcome!

I've done the most minimal work to port this to Python 3.

To run it in development mode: ``hatch run pynche``.


Copyright
=========

Copyright (C) 1997-2026 Barry A. Warsaw

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Table of Contents and Index
===========================

* :ref:`genindex`

.. toctree::
    :glob:

    using
    NEWS
