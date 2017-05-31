#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="clang_hook",
    version="0.1",
    description="An hook to replace a C compiler by a custom toolchain based on llvm. This is usefull for "
                "automatic compilation, eg. with CMake which don,t care about how we want to compile.",
    url="https://gitlab.marc-chevalier.com/Stage-4A-Roma/scripts",
    author="Marc Chevalier",
    author_email="pro@marc.chevalier",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Compilers",
        "Topic :: Utilities",

    ],
    install_requires=[
    ],
    packages=[
        "clang_hook",
        "lib_hook",
        "over_make",
    ],
    entry_points={
        "console_scripts": [
            "clang-hook = clang_hook.main:main",
            "profiled-clang-hook = clang_hook.main:profiled_main",
            "over-make = over_make.main:main",
        ],
    },
)
