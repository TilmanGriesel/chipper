.PHONY: build-dev run-dev stop-dev clean-dev dev

IMAGE_NAME = api-dev
CONTAINER_NAME = api-dev
DEV_DOCKERFILE = Dockerfile.dev

WEB_BASE_DIR = src

OS_TYPE := $(shell uname -s)
ifneq (,$(findstring MINGW,$(OS_TYPE)))
    export MSYS_NO_PATHCONV=1
endif

build-dev:
	docker build -f $(DEV_DOCKERFILE) -t $(IMAGE_NAME) .

run-dev:
	docker run \
		--env-file .env \
		-v "$(CURDIR)/src:/app/src" \
		-p 8000:8000 \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

stop-dev:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

clean-dev: stop-dev
	docker rmi $(IMAGE_NAME) || true

dev: stop-dev build-dev run-dev
