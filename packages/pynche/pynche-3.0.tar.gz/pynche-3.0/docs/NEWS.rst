===============
 Release Notes
===============

3.0 (2026-01-08)
================
* Major modernization sweep.
* Reorganize the documentation, add this NEWS file, and publish on `ReadTheDocs
  <https://pynche.readthedocs.io/en/latest/>`_.
* Drop support for Python 3.9.
* Adopt `Hatch <https://hatch.pypa.io/latest/>`_ for project management and drop PDM.
* Drop ``flake8``, ``isort``, and ``blue`` in favor of `ruff <https://astral.sh/ruff>`_ and `pyrefly
  <https://pyrefly.org/en/docs/>`_.
* Liberally add type hinting.
* Update copyright years.
* Add a minimal test suite.


2.0a1 (2022-06-11)
==================

* Added images to the README for better documentation.
* Updated README with improved content.


2.0a0 (2022-06-11)
==================

This is the first release of Pynche as a standalone package, extracted from
the Python standard library's Tools directory.

* Ported to Python 3.
* Reorganized as a standalone repository with proper package structure.
* Modernized build system using PDM.
* Cleaned up imports throughout the codebase.
* Added comprehensive README.md documentation.
* Fixed initfile writing issues.
* Improved error reporting for Tkinter when default root is absent.
* Fixed ``__eq__``, ``__lt__`` and other comparison implementations.
* Removed long-commented dead code.
* Various bug fixes and code cleanups accumulated over the years.


Pre-History
===========

Before becoming a standalone package, Pynche lived in the CPython source tree
under ``Tools/pynche``.

* `What's New In Python 3.11 <https://docs.python.org/3/whatsnew/3.11.html#removed>`_
  — Pynche was removed from ``Tools/scripts`` and moved to independent development.

* `Pynche 1.0 Announcement (May 1999)
  <https://mail.python.org/pipermail/python-announce-list/1999-May/000019.html>`_ — Pynche 1.0
  released as an update to the version distributed with Python 1.5.2, adding support for loading
  different color name databases (web-safe, HTML 4.0, browser-safe, and X11 color names).
