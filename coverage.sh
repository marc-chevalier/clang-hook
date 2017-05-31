#!/bin/bash
python3-coverage run --source=clang_hook,lib_hook,over_make run_tests.py
python3-coverage html
xdg-open htmlcov/index.html

