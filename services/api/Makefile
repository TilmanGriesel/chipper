.PHONY: dev build-dev run-dev stop-dev clean-dev

IMAGE_NAME = api-dev
CONTAINER_NAME = api-dev
DEV_DOCKERFILE = Dockerfile.dev

WEB_BASE_DIR = src

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
BACKEND_NETWORK = chipper_backend

dev: stop-dev build-dev run-dev

build-dev:
	$(CONTAINER_CMD) build -f $(DEV_DOCKERFILE) -t $(IMAGE_NAME) .

run-dev:
	$(CONTAINER_CMD) run \
		--rm  \
		--name chipper-api-dev \
		--hostname api \
		--env-file .env \
		-v "$(CURDIR)/src:/app/src:z" \
		-p 21434:8000 \
		--name $(CONTAINER_NAME) \
		--network=$(NETWORK) \
		$(IMAGE_NAME)
	$(CONTAINER_CMD) network connect $(BACKEND_NETWORK) $(CONTAINER_NAME)

stop-dev:
	$(CONTAINER_CMD) stop $(CONTAINER_NAME) || true
	$(CONTAINER_CMD) rm $(CONTAINER_NAME) || true

clean-dev: stop-dev
	$(CONTAINER_CMD) rmi $(IMAGE_NAME) || true
