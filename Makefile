.PHONY: install test lint demo serve build clean

install:   ## create venv + install (editable, with dev extras)
	python3 -m venv .venv && ./.venv/bin/pip install -e ".[dev]"

test:      ## run the test suite
	./.venv/bin/pytest

lint:      ## run the ruff lint gate
	./.venv/bin/ruff check src tests

demo:      ## run the end-to-end trading-agent demo
	./.venv/bin/python examples/trading_agent.py

serve:     ## launch the control API + dashboard (http://127.0.0.1:8787)
	./.venv/bin/sentinel serve

build:     ## build the wheel + sdist
	./.venv/bin/python -m build

clean:     ## remove build artifacts + local data
	rm -rf dist build *.egg-info data/*.db data/*.db-wal data/*.db-shm
