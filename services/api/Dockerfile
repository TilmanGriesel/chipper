FROM python:3.12-slim

ARG VERSION=latest
ENV APP_VERSION=$VERSION

ENV HAYSTACK_TELEMETRY_ENABLED=False

ARG BUILD_NUM=0
ENV APP_BUILD_NUM=$BUILD_NUM

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# First copy example, and then use user system prompt if it can be found
COPY .systemprompt.example /app/.systemprompt
COPY .systempromp[t] /app/.systemprompt

ENV PYTHONPATH=/app/src

ENTRYPOINT ["gunicorn"]
CMD ["--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "src.main:app"]
