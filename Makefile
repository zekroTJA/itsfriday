PY = py -3.7 # for windows - ensure python version 3.7 
# PY = python3   # for linux
# PY = python3.7 # for linux - ensure python version 3.7
# PY = python3.8 # for linux - ensure python version 3.8

CONFIG = "$(CURDIR)/config.json"

.PHONY: _make deps deps-user debug run

_make:
	@echo "Available targets:"
	@echo "  deps       - install or update required dependencies"
	@echo "  deps-user  - same as deps, but in usermode (--user)"
	@echo "  debug      - run with debug config in configs folder"
	@echo "  run        - run with default config file (./config.json)"
	@echo "  CONFIG="myconf.json" run"
	@echo "             - run with custom config file"

deps:
	$(PY) -m pip install -U -r $(CURDIR)/requirements.txt

deps-user:
	$(PY) -m pip install -U -r --user $(CURDIR)/requirements.txt

debug:
	$(PY) $(CURDIR)/main.py -c $(CURDIR)/config/private.config.json

run:
	$(PY) $(CURDIR)/main.py -c $(CONFIG)