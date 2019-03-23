PY = py # this must be 'python3' for linux systems

.PHONY: _make deps debug

_make: deps

deps:
	$(PY) -m pip install -U -r requirements.txt

debug:
	$(PY) ./main.py -c ./config/private.config.json