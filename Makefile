.DEFAULT_GOAL := web-client-serve

.PHONY: local-es-up local-es-down local-es-down-volumes embed-gui rest-api-serve \
        web-client-cli web-client-serve web-client-build-css \
        web-client-watch-css web-client-build scrape-and-embed scraper-util embed-scraper-output

VENV_ACTIVATE = . venv/bin/activate
PYTHON = python
TAILWIND = npx tailwindcss
WEB_BASE_DIR = src/web/
CSS_INPUT = static/main.css
CSS_OUTPUT = static/style.css
TAILWIND_CONFIG = tailwind.config.js
SCRAPER_UTIL = utils/scraper/scrape_web.py
SCRAPER_OUTPUT = data
PYTHONPATH = PYTHONPATH=.
PID_FILE = .server.pid

venv:
	@$(VENV_ACTIVATE)

local-es-up:
	@cd docker && docker compose up -d

local-es-down:
	@cd docker && docker compose down

local-es-down-del-volumes:
	@cd docker && docker compose down --volumes

embed-gui:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) main.py || (echo "Embedding client failed to start"; exit 1)

scrape-and-embed: scraper-util embed-scraper-output

scraper-util:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) $(SCRAPER_UTIL) || (echo "Scraper failed to start"; exit 1)

embed-scraper-output:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) main.py --path $(SCRAPER_OUTPUT) || (echo "Embedding client failed to start"; exit 1)

rest-api-serve:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) src/web/rest_server.py || (echo "REST API server failed to start"; exit 1)

web-client-serve:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) src/web/client_web_server.py || (echo "Web client server failed to start"; exit 1)

web-client-cli:
	@$(VENV_ACTIVATE) && $(PYTHONPATH) $(PYTHON) src/web/client_cli.py || (echo "CLI client failed to start"; exit 1)

web-client-build-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --config $(TAILWIND_CONFIG) || (echo "CSS build failed"; exit 1)

web-client-watch-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --watch --config $(TAILWIND_CONFIG) || (echo "CSS watch failed"; exit 1)

web-client-build: web-client-build-css web-client-web
