===================================
 Developer guide for ``clang-hook``
===================================

-----------------------
Or how to deceive CMake
-----------------------
:Author: Marc Chevalier
:Date: apr. 2017


Introduction
============

I will explain basic architecture, missing features and some other things about
the inside of ``clang-hook``.

First, a warning. If your compilation crashes with an ugly message, checks
thoughtfully if your configuration is valid. Of course, ``clang-hook`` is far to
be flawless, but most of the times I got an error, it was a mistake in my
configuration. However, errors should have a nice display, or a maybe the
behavior of ``clang-hook`` might be more lenient. So, a mistake don't mean there
is nothing to do.

Debugging
=========

The ``--hook`` allows to give some parameters to ``clang-hook``. There is only
one option for now: ``--hook debug``. It is meant to print debugging infos. Feel
free to use it and extend it.

Architecture
============

The entry point is ``main()`` in ``main.py``.

The beginning of this function is

.. code:: python

  hook_config = lib_hook.HookConfig()
  logger = lib_hook.Logger()
  args = lib_hook.init_hook_parser().parse_args()

  debug = args.hook is not None and "debug" in args.hook

  hook_config.init(logger.info, arg_path=args.hook_config, debug=debug)
  logger.init(args, hook_config)

  compiler = lib_hook.Compiler(args, hook_config, logger)

as you see, everything is first declared, then initialized at the right moment.

Argument Parser
---------------

I used ``argparse`` which is standard and very handy. The only trick is that I
use custom actions to easily get lists of include directories, warnings or link
flags.

Configuration
-------------

The configuration file is parsed only once. It is done by giving the
configuration as a parameter whenever it is required. However, it is still
possible to parse it again. The goal is to have an easy way to have several
kinds of configuration file. But for now, it's a trap. If it seems that only one
configuration file is enough, I probably change a bit the architecture of the
configuration module to ensures that parsing will be done only once.

Logger
------

Loggers are initialized after everything else. Indeed, loggers needs
configuration to know where to log. However, there is a small trick which keeps
logs in a list before initialization and as soon as the initialization is done,
everything is dumped in logs. However, a panic before initialization won't be
logged. Too bad!


Future development
==================

Choose the compiler
-------------------

Add an option in config file to set the clang version to use.
