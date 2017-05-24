# clang-hook
How to deceive cmake and make llvm test suite computer scientist-friendly again.

## Introduction

This software is made for computer scientist who want to configure the compilation of llvm test-suite (eg. using their own passes) with the new test architecture.

## History

Remember the good ol' time when, to compile with your own configuration you just had to write TEST.name.Mafile and TEST.name.report? Now, with this CMake-based architecture, it's impossible. Cmake write all the makefiles for you and there is not way to tell him what you want. `clang-hook` is made for you!

In fact, until LLVM 3.7, you could just use `configure` to use the old architecture (maybe with a little trick to disable the warning). But since 3.8, `configure` contains nothing but the warning.

You just have to configure cmake so that it use `clang-hook` as the C compiler and all you have to do is to write the configuration file for `clang-hook`.

## Dependancies

* LLVM version you want (obviously). `clang-hook` will use `clang`, `opt` and `llc`.
* Python3 (>=3.5) and its standard library.

That's all!

## Install it!

Clone the repo, and `make install` (global install, need root (not recommended) or a virtualenv) or `make localinstall` (local install, I use that).

## Use it!

There is a user documentation.

### tl;dr

1. Does it work? Yes, absolutely! I used it a lot of time. 

2. How does it work? Well... you really want to know? In this case, there is developper documentation. Otherwise, keep away for this black magic.

3. How do I use it?

  ```bash
  export CC=clang-hook
  export CXX=clang-hook
  cmake path/to/source/tree
  make
  ```

  And obviously, write config files. Look at the examples.
  
4. Can I run `make -j4`. No... sorry. `clang-hook` don't like to be run multiple times on the same configuration at the same time. But there is a solution. Use instead
  ```bash
  over-make make -j4
  ```

5. What is this `over-make` anyway? It is a program that synchronises `clang-hook` (and makes them run even faster!). There is a specific documentation.
  You will need to know how to use `clang-hook` anyway. It achieves its task by communicating with `clang-hook` using a server-client architecture. In this case, `clang-hook`
  run in network mode, but don't worry, it works the same way for the user.


## Contributing

You want to contribute?! Great! There is a few constraints. First, use only the standard Python3 library and no Python3 version newer than what we find in Ubuntu packages (or other mainstream distribution). I want to keep it easy to install and relatively easy to use.

If you could follow the PEP-8, it would be great.
