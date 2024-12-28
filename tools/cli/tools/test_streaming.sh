curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: DEMO-API-KEY-123" \
  -d '{
    "model": "llama3.2",
    "messages": [
      {"role": "user", "content": "What is machine learning?"}
    ],
    "options": {
      "index": "default"
    }
  }' \
  --no-buffer
