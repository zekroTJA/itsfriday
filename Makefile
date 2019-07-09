PYTHON_WIN = py
PYTHON_UNX = python3

ifeq ($(OS),Windows_NT)
	PY = $(PYTHON_WIN)
else
	PY = $(PYTHON_UNX)
endif


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
	$(PY) $(CURDIR)/itsfriday/main.py -c $(CURDIR)/config/private.config.json

run:
	$(PY) $(CURDIR)/itsfriday/main.py -c $(CONFIG)