PY = py # this must be 'python3' for linux systems

CONFIG="$(CURDIR)/config.json"

.PHONY: _make deps debug run

_make: deps

deps:
	$(PY) -m pip install -U -r requirements.txt

debug:
	$(PY) $(CURDIR)/main.py -c $(CURDIR)/config/private.config.json

run:
	$(PY) $(CURDIR)/main.py -c $(CONFIG)