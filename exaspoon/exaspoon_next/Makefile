UV ?= uv
VENV ?= .venv
PYTHON ?= $(abspath $(VENV))/bin/python
UV_CACHE_DIR ?= $(abspath .uv-cache)
USE_UV ?= 0

.PHONY: agent-install agent-run agent-test

agent-install:
	@if [ "$(USE_UV)" = "1" ] && command -v $(UV) >/dev/null 2>&1; then \
		cd agents && UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) pip sync requirements.txt || ( $(MAKE) $(PYTHON) && $(PYTHON) -m pip install -r agents/requirements.txt ); \
	else \
		$(MAKE) $(PYTHON); \
		$(PYTHON) -m pip install -r agents/requirements.txt; \
	fi

agent-run:
	@if [ "$(USE_UV)" = "1" ] && command -v $(UV) >/dev/null 2>&1; then \
		cd agents && UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run python -m src.mas.agents.main; \
	else \
		cd agents && $(PYTHON) -m src.mas.agents.main; \
	fi

agent-test:
	@if [ "$(USE_UV)" = "1" ] && command -v $(UV) >/dev/null 2>&1; then \
		UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run pytest tests/; \
	else \
		$(PYTHON) -m pytest tests/; \
	fi
