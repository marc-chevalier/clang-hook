
PYTHON=python3

all:
	$(PYTHON) setup.py

install:
	$(PYTHON) setup.py install

localinstall:
	$(PYTHON) setup.py install --user

.PHONY: all install localinstall
