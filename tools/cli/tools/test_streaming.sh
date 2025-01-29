curl -X POST http://localhost:21434/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: EXAMPLE_API_KEY" \
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
