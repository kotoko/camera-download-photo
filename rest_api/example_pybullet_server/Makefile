SHELL = /bin/bash
VENVDIR = venv
PYTHON = python3 

all: clean prepare run

prepare:
	$(PYTHON) -m venv $(VENVDIR)
	source $(VENVDIR)/bin/activate && pip install --upgrade pip
	source $(VENVDIR)/bin/activate && pip install -r requirements.txt

run:
	source $(VENVDIR)/bin/activate && $(PYTHON) simple_server.py

clean:
	$(RM) -r $(VENVDIR)

.PHONY: all prepare run clean
