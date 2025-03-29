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

# Container engine configuration
ifndef CONTAINER_ENGINE
    DOCKER := $(shell command -v docker 2>/dev/null)
    PODMAN := $(shell command -v podman 2>/dev/null)

    ifneq ($(DOCKER),)
        CONTAINER_ENGINE := $(DOCKER)
    else ifneq ($(PODMAN),)
        CONTAINER_ENGINE := $(PODMAN)
    else
        $(error No container engine found. Please install docker or podman)
    endif
endif

CONTAINER_CMD := $(shell basename $(CONTAINER_ENGINE))
$(info Using container engine: $(CONTAINER_CMD))

# Network configuration
NETWORK = chipper_network

build-dev:
	$(CONTAINER_CMD) build -f $(DEV_DOCKERFILE) -t $(IMAGE_NAME) .

run-dev:
	$(CONTAINER_CMD) run \
		--rm  \
		--name chipper-web-dev \
		--env-file .env \
		-v "$(CURDIR)/src:/app/src:z" \
		-p 21200:5000 \
		--name $(CONTAINER_NAME) \
		--network=$(NETWORK) \
		$(IMAGE_NAME)

stop-dev:
	$(CONTAINER_CMD) stop $(CONTAINER_NAME) || true
	$(CONTAINER_CMD) rm $(CONTAINER_NAME) || true

clean-dev: stop-dev
	$(CONTAINER_CMD) rmi $(IMAGE_NAME) || true

dev: stop-dev build-dev run-dev

build-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --config $(TAILWIND_CONFIG) || (echo "CSS build failed"; exit 1)

build-watch-css:
	@cd $(WEB_BASE_DIR) && $(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --watch --config $(TAILWIND_CONFIG) || (echo "CSS watch failed"; exit 1)
