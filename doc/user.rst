==============================
 User guide for ``clang-hook``
==============================

-----------------------
Or how to deceive CMake
-----------------------
:Author: Marc Chevalier
:Date: apr. 2017


Introduction
============

CMake allows us to compile easily big projects by handling everything about the 
compilation. But sometimes, we want a precise compilation process. For instance,
we might want to be able to compile the cmake-based LLVM test-suite with custom
passes. And we don't want to modify every CMake... 

``clang-hook`` is a small program made for being used by CMake as a C compiler.
Of course, ``clang-hook`` isn't a compiler. All it does is to parse parameters
and invoke real compilers. In fact, the compilation chain looks like:

1. ``clang -emit-llvm ...``: .c -> .bc
2. ``opt ...``: .bc -> .bc
3. ``llc ...``: .bc -> .o or .bc -> .s
4. ``clang ...``: .o -> native executable (linking)

This way, we can give any parameters to ``opt``.


*NB: each time you will see "the behavior is undefined", it means, "don't do
it!".*

Requirement
===========

* Python >= 3.5 (only the standard library)
* clang, llvm (opt, llc) in the current path

Features
========

``clang-hook`` was designed to replace gcc (or clang) in CMake-based
compilations. Consequently, it can compile to obj file (with -c  option), link
obj files to a native executable or do the both at one.

Internally, during the compilation (.c -> .o) phase, each file goes through step
1 to 3 (cf. supra) individually. Only linking involve multiple inputs.

By default, ``clang-hook`` generate a .bc and .o file for each input .c file and
do not remove it. But, it seems cmake-based compilation delete them.

Since ``clang-hook`` invoke programs of the $PATH, if is really easy to change
the current version of LLVM it rely on.

Basic Usage
===========

Install
-------

``python3 setup.py install`` (except in a virtualenv, you might need to be
root)

or

``python3 setup.py install --user`` (local installation)

You should have a ``clang-hook`` command available in the shell. It also add
``over-make`` and ``profiled-clang-hook``, cf. the adequate documentations
(resp. ``over-make`` user guide and developer guide).

Use with CMake
--------------

``cmake path/to/the/sources -DCMAKE_C_COMPILER=clang-hook``

Now, when doing ``make``, ``clang-hook`` will be call instead of the C compiler.
Isn't it magical? The other good news is that you will not have to reconfigure
when you change the config of ``clang-hook`` since it is still the same command.

**Beware! clang-hook is not thread safe! Really not. Don't even try a
``make -jn`` or you will regret it!**

In fact, it will totally messed up your outputs and crash the program. However,
it is probably possible (though not guaranteed) that if there is not output, no
report and no log, it will work with multiple instances.

On the other hand, running two instances of ``clang-hook`` with two separate
config files which does not share any file is safe.

With nothing
------------

Of course, it can be use alone. The advantage is the same: when testing
compilation with a lot of flags, it can lighten things a lot.


Configuration
=============

Where are they ?
----------------

By default, it will look at, in this order, from the most particular to the most
general.

1. $CLANG_HOOK_CONFIG
2. ./clang-hook.conf
3. $HOME/clang-hook.conf
4. /etc/clang-hook/clang-hook.conf

With the option ``--hook-config file`` it will look at this location in first.
However, if the file isn't found, the other paths are scanned.

Most people who need this hook won't be happy with ONE config, thus, option 3
and 4 are probably bad ideas. Option 2 seems good, but in cmake-based
compilation, the compiler is called from a large variety of location.

During configuration, we can five the ``--hook-config`` option to
``clang-hook``. With an abolute path, there will be no problems. But if we
change the location of the configuration file (not the content), it would be
necessary to reconfigure cmake.

With the option 1, we can change the location when we want, there is nothing
particular with the cmake configuration. It is the best way with cmake-based
compilation to points to the configuration file to use. It just need to not 
forget to set the variable.

If not configuration is found (or incomplete), each parameter have boring
default values.

tl;dr
~~~~~~~~~~~~~
Set ``$CLANG_HOOK_CONFIG`` to contain the path of the configuration file.

The syntax
----------

Configuration are json files and look like:


.. code:: json

  {
    "link_flags": ["-lflag"],
    "passes": ["-hello"],
    "load": ["/.../lib/LLVMHello.so"],
    "error_log": "/.../error.log",
    "info_log": "/.../info.log",
    "debug_log": "/.../debug.log",
    "log": true,
    "output": "/.../output.json",
    "filters": [
      {
          "name": "hellos",
          "stages": ["opt"],
          "pattern": "(?<=Hello: )[A-Za-z_][A-Za-z_0-9]*",
          "type": "string",
          "mode": "lookaround",
          "summary": "append"
      },
      {
          "name": "hellos2",
          "stages": ["opt"],
          "pattern": "Hello: (?P<name>[A-Za-z_][A-Za-z_0-9]*)",
          "type": "string",
          "mode": "group",
          "group": "name",
          "summary": "append"
      }
    ]
  }

The semantic
------------

For safety, every paths must be absolute. Undefined behavior otherwise.

``link_flags``
~~~~~~~~~~~~~~

:Type: list of strings
:Default: []
:Semantic: Flags given to the linker. If the linker is not invoked, it is 
  ignored

``passes``
~~~~~~~~~~~~~~

:Type: list of strings
:Default: []
:Semantic: Passes to be run by ``opt``.

``load``
~~~~~~~~~~~~~~

:Type: list of strings (paths)
:Default: []
:Semantic: Paths to the dynamic passes (.so) to load by opt. ``-load`` flags are
  the first given to ``opt``
:Warning: The passes must be compiled for the right version of llvm.

``error_log``
~~~~~~~~~~~~~~

:Type: string (path)
:Default: "error.log"
:Semantic: Path to the file use to log errors. Undefined behavior if equal to
  another log file.

``info_log``
~~~~~~~~~~~~~~

:Type: string (path)
:Default: "info.log"
:Semantic: Path to the file use to log infos. Undefined behavior if equal to
  another log file.

``debug_log``
~~~~~~~~~~~~~~

:Type: string (path)
:Default: "debug.log"
:Semantic: Path to the file use to log debug messages. Undefined behavior if 
  equal to another log file.

``log``
~~~~~~~~~~~~~~

:Type: boolean
:Default: true
:Semantic: Whether ``clang-hook`` should log or not. If false, paths to log
  files are ignored.

``output_file``
~~~~~~~~~~~~~~~

:Type: string (path)
:Default: None
:Semantic: Where to store raw output (stdout). If omitted, output is printed on
  stdout.

``output_stages``
~~~~~~~~~~~~~~~~~

:Type: list of string (among "clang", "opt", "llc", "link")
:Default: ["clang", "opt", "llc", "link"]
:Semantic: Which stage you want to save the output. Repetitions are ignored.


``filters``
~~~~~~~~~~~

This is much more complex. This feature allows statistic to be computed in the
way of former TEST.xxx.report files. There are two formats for the filters
depending on how one want to interpret the regex.

They look like


.. code:: json

  {
      "name": "hellos",
      "stages": ["opt"],
      "pattern": "(?<=Hello: )[A-Za-z_][A-Za-z_0-9]*",
      "type": "string",
      "mode": "lookaround",
      "summary": "append"
  }

or

.. code:: json

  {
      "name": "hellos2",
      "stages": ["opt"],
      "pattern": "Hello: (?P<name>[A-Za-z_][A-Za-z_0-9]*)",
      "type": "string",
      "mode": "group",
      "group": "name",
      "summary": "append"
  }
  
  
**There cannot be any missing field. It would be an error.**
  
Each filter allows the extraction of a value (integer, float, boolean or 
string) for each process (often, run ``opt`` on a single file). These results
are stored for further computations. However, ``clang-hook`` has one feature to
make global statistics. When linking several .o files, ``clang-hook`` use all
values collecting during the generations of these files to make a global value.
Usually, it's simply the sum of collected integers.


**Beware! Since ``clang-hook`` runs at the level of each file compilation, it 
does not have any idea of the overall process. Consequently, it loads output 
and report files modifies the content and save them. If you don't change (or
delete) these files between two runs of ``make``, ``clang-hook`` will just 
append new informations.**

``name``
````````
:Type: string
:Semantic: The name of the filter. If two filters have the same name, the
  behavior is undefined.
:Warning: A filter is entirely identified by its name. It is undefined behavior
  to have multiple filters with the same name.

``stages``
``````````
:Type: list of string (among "clang", "opt", "llc", "link")
:Semantic: The stages where this filter works. Often ["opt"].

``type``
````````
:Type: string among "string", "int", "bool", "float"
:Semantic: The type of the matched string. The result matched will be casted in
  the adequate type. For instance, the regex ``(?<=Something: )[1-9][0-9]*``
  will match decimal representation of integers. If ``type`` is ``int``,
  the result will be interpreted and store as an integer, allowing computations
  such mean and sum.

``summary``
```````````
:Type: string among "append", "mean", "sum", "number", "or" and "and"
:Semantic: the action to build the overall summary. "append" will construct a
  list from each matching value. "number" will count the number of matches.
  These actions is always valid. "mean" and "sum" are pretty clear. They are
  only valid when the field ``type`` is a arithmetic type ("int" or "float").
  "or" and "and" are valid onyl for "bool".


``pattern``
```````````
:Type: string (a python-valid regex)
:Semantic: The regex to match on the output. The exact way this regex is used
  depends on ``mode`` (cf.infra).

``mode``
````````
:Type: string among "lookaround", "group"
:Semantic: If ``mode`` is "lookaround", the whole match will be used. The name
  come from the fact you probably need positive/negative lookahead/-behind to be
  sure to get the right line.
  
  If ``mode`` is "group" only the group whose the name is given by the field 
  ``group`` (cf. infra) will be used.
  
  The two ways are pretty equivalent. Pick your favorite one! The "group" mode
  is probably better if there are two filters with the same regex but which want
  different groups.

``group``
`````````
:Type: string
:Semantic: If ``mode`` is "group", it names the group to extract (cf. supra). 
  Otherwise, the behavior is undefined. If the name is not the name of a group
  of the regex, the behavior is undefined.


Outputs
=======

There are two kinds of output files: one to store stdout and the other one to
store the matches of the filters. Both are meant to be easily processable by
the user.

outpout

.. code:: json

  {
      "compils": [
          {
              "input_file": "test.c",
              "output_file": "test.o",
              "stdout": "",
              "stage": "clang"
          },
          {
              "input_file": "test.c",
              "output_file": "test.o",
              "stdout": "Hello1: main\n",
              "stage": "opt"
          },
          {
              "input_file": "test.c",
              "output_file": "test.o",
              "stdout": "",
              "stage": "llc"
          },
          {
              "input_file": "test2.c",
              "output_file": "test2.o",
              "stdout": "",
              "stage": "clang"
          },
          {
              "input_file": "test2.c",
              "output_file": "test2.o",
              "stdout": "Hello1: f\n",
              "stage": "opt"
          },
          {
              "input_file": "test2.c",
              "output_file": "test2.o",
              "stdout": "",
              "stage": "llc"
          },
          {
              "input_file": [
                  "test.o",
                  "test2.o"
              ],
              "output_file": "foo",
              "stdout": "",
              "stage": "link"
          }
      ],
      "config": {
          ... content of the config file ...
      }
  }
  
and report file

.. code:: json

  {
      "summary": {
          "executable": "foo",
          "results": [
              {
                  "result": 2,
                  "name": "hellos_count"
              },
              {
                  "result": [
                      "main",
                      "f"
                  ],
                  "name": "hellos"
              },
              {
                  "result": [
                      "main",
                      "f"
                  ],
                  "name": "hellos2"
              }
          ],
          "obj_files": [
              "test.o",
              "test2.o"
          ]
      },
      "compils": [
          {
              "c_file": "test.c",
              "matches": [
                  {
                      "name": "hellos",
                      "match": "main"
                  },
                  {
                      "name": "hellos2",
                      "match": "main"
                  },
                  {
                      "name": "hellos_count",
                      "match": 1
                  }
              ],
              "obj_file": "test.o",
              "stage": "opt"
          },
          {
              "c_file": "test2.c",
              "matches": [
                  {
                      "name": "hellos",
                      "match": "f"
                  },
                  {
                      "name": "hellos2",
                      "match": "f"
                  },
                  {
                      "name": "hellos_count",
                      "match": 1
                  }
              ],
              "obj_file": "test2.o",
              "stage": "opt"
          }
      ],
      "config": {
          ... content of the config file ...
      }
  }
  
We can see that they both embed the configuration. This way they can be
processed alone (to have access to the passes) and to ensure consistency of
results (they come from the same compilation process).


