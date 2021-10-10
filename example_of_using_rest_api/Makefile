SHELL = /bin/bash
VENVDIR = venv
PYTHON = python3

all: clean prepare

prepare:
	$(PYTHON) -m venv $(VENVDIR)
	source $(VENVDIR)/bin/activate && pip install --upgrade pip
	source $(VENVDIR)/bin/activate && pip install -r requirements.txt
	chmod +x recognize.py
	chmod +x send-config.py
	chmod +x pybullet_server_with_balls.py

runPybulletServer:
	source $(VENVDIR)/bin/activate && $(PYTHON) pybullet_server_with_balls.py

clean:
	$(RM) -r $(VENVDIR)

.PHONY: all prepare clean runPybulletServer
