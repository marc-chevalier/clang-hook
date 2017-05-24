==================================
 Developer guide for ``over-make``
==================================

-------------------------------------
Or how to deceive CMake thread-safely
-------------------------------------
:Author: Marc Chevalier
:Date: may 2017


Introduction
============

The basic idea is to avoid doing a lot of times the same thing. Indeed, when you
do ``make``, ``clang-hook`` is launched a lot of times. Each one initialize a
command line argument parser, parse the config, parse the output and report, add
informations, print it again... It's a lot of work. 

So, ``over-make`` do all these things once. Then it communicates with
``clang-hook`` via sockets to do... stuff...

Debugging
=========

The ``--over`` allows to give some parameters to ``clang-hook``. There is only
one option for now: ``--over debug``. It is meant to print debugging infos. Feel
free to use it and extend it.

Architecture
============

``over-make`` spawn a server and register its address in ``$OVER_CLANG_ADDR``
and the port in ``$OVER_CLANG_PORT``. Then, it runs the given command (typically
``make``).

Each instance of ``clang-hook`` will look
for ``$OVER_CLANG_ADDR``. If it exists, it will run in network mode, otherwise,
it runs standalone mode.

Initialization is a lot different:


- The logger is only a client logger: it sends all to ``over-make`` to be
  logged;
- The arguments are sent to ``over-make`` to be parsed and the namespace is
  returned;
- Instead of looking for the config and parsing it, it is directly requested and
  sent;
- The output handler is also a client (like the logger), thus, report and output
  files are never parsed and written only once.

Communications format
=====================

General informations
--------------------

On the first 4 bytes, there is the size of the incoming message encoded in big
endian (why big? why not...). On the following bytes there is the content
encoded with pickle.

Requests formats
----------------

Request are dictionaries with two fields: ``"request_type"`` and ``"args"``. 
``"request_type"`` is a string describing the kind of request. There are:

- output
- report
- summary
- parse_args
- log
- get_config

``"args"`` contains the arguments for the request. In the soft, it is always a
dictionary
