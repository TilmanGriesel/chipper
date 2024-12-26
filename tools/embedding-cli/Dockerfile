FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/data

# Set environment variables (optional defaults)
# ENV ES_URL=http://host.docker.internal:9200
# ENV OLLAMA_URL=http://host.docker.internal:11434
# ENV EMBEDDING_MODEL=your_embedding_model

ENTRYPOINT ["python", "src/main.py"]
CMD []