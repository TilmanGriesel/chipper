FROM python:3.12-slim

ARG VERSION=latest
ENV APP_VERSION=$VERSION

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENTRYPOINT ["python", "src/main.py"]
CMD ["--output-dir=/app/data", "--batch-size=5", "--delay=2.0"]
