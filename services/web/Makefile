.PHONY: build-dev run-dev stop-dev clean-dev dev build-css build-watch-css

IMAGE_NAME = web-dev
CONTAINER_NAME = web-dev
DEV_DOCKERFILE = Dockerfile.dev

TAILWIND = npx tailwindcss
WEB_BASE_DIR = src
CSS_INPUT = static/main.css
CSS_OUTPUT = static/dist/index.css
TAILWIND_CONFIG = tailwind.config.js

OS_TYPE := $(shell uname -s)
ifneq (,$(findstring MINGW,$(OS_TYPE)))
    export MSYS_NO_PATHCONV=1
endif


build-dev:
	docker build -f $(DEV_DOCKERFILE) -t $(IMAGE_NAME) .

run-dev:
	docker run \
		--rm  \
		--name chipper-web-dev \
		--env-file .env \
		-v "$(CURDIR)/src:/app/src" \
		-p 21200:5000 \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

stop-dev:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

clean-dev: stop-dev
	docker rmi $(IMAGE_NAME) || true

dev: stop-dev build-dev run-dev

build-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --config $(TAILWIND_CONFIG) || (echo "CSS build failed"; exit 1)

build-watch-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --watch --config $(TAILWIND_CONFIG) || (echo "CSS watch failed"; exit 1)

