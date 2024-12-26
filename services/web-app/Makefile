.DEFAULT_GOAL := build-css

.PHONY: build-css build-watch-css

VENV_ACTIVATE = . venv/bin/activate
PYTHON = python
TAILWIND = npx tailwindcss
WEB_BASE_DIR = src
CSS_INPUT = static/main.css
CSS_OUTPUT = static/style.css
TAILWIND_CONFIG = tailwind.config.js

build-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --config $(TAILWIND_CONFIG) || (echo "CSS build failed"; exit 1)

build-watch-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --watch --config $(TAILWIND_CONFIG) || (echo "CSS watch failed"; exit 1)

