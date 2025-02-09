FROM python:3.12-slim

ARG VERSION=latest
ENV APP_VERSION=$VERSION

ARG BUILD_NUM=0
ENV APP_BUILD_NUM=$BUILD_NUM

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV ENV_MANAGER_BLACKLIST=docker/.env

ENTRYPOINT ["python", "src/main.py"]
CMD []
