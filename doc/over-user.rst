=============================
 User guide for ``over-make``
=============================

-------------------------------------
Or how to deceive CMake thread-safely
-------------------------------------
:Author: Marc Chevalier
:Date: may 2017


Introduction
============

You should be familiar with ``clang-hook`` before reading this, otherwise, you
will cough up bloop.

As said in the ``clang-hook`` user guide, ``clang-hook`` is not thread safe.
That why I wrote ``over-make``: it make ``clang-hook`` thread-safe.

The idea is to run one instance of ``over-make`` above all ``clang-hook`` to
manage concurrency.

Basic Usage
===========

Install
-------

It is installed with ``clang-hook``, don't worry !

Use with CMake
--------------

First, configure project as explained in the user guide. But instead of running
``make``, you run ``over-make make``. Of course, it is not very interesting,
though it already can make you save time. But you can also run ``over-make make
-j4`` (or whatever -j you want). Isn't it cool?

More generally, you can run any command, but if there are multiple argument, you
should use quotation marks: ``over-make "a very long command"``. Only ``-jn``
doesn't need quotation marks: since this option is very usual, it is handle
separately.


Configuration
=============

Where are they ?
----------------

Globally, he same rules that for ``clang-hook`` apply. Though, there are small
differences:

- the environment variable for the config path is ``OVER_MAKE_CONFIG``
- the default name of the config file is ``over-make``

tl;dr
~~~~~
Set ``$OVER_MAKE_CONFIG`` to contain the path of the configuration file.

The syntax
----------

Once again, it is quite similar, there only are:

- error_log
- info_log
- debug_log
- log
- output_file
- report_file
- hook_config

The last is the path to the config file. It is searched only by ``over-make``
and not by ``clang-hook``.

Command line arguments
======================

There are a few command line arguments:

- ``--hook-config path``: path to the configuration file of ``clang-hook``
- ``--over-config path``: path to the configuration file of ``over-make``
- ``--over flag``: flag for ``over-make`` the only currently supported is
  ``debug``


