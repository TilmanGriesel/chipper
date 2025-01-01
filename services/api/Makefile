.PHONY: dev build-dev run-dev stop-dev clean-dev

IMAGE_NAME = api-dev
CONTAINER_NAME = api-dev
DEV_DOCKERFILE = Dockerfile.dev

WEB_BASE_DIR = src

OS_TYPE := $(shell uname -s)
ifneq (,$(findstring MINGW,$(OS_TYPE)))
    export MSYS_NO_PATHCONV=1
endif

dev: stop-dev build-dev run-dev

build-dev:
	docker build -f $(DEV_DOCKERFILE) -t $(IMAGE_NAME) .

run-dev:
	docker run \
		--rm  \
		--name chipper-api-dev \
		--env-file .env \
		-v "$(CURDIR)/src:/app/src" \
		-p 21210:8000 \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

stop-dev:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

clean-dev: stop-dev
	docker rmi $(IMAGE_NAME) || true

