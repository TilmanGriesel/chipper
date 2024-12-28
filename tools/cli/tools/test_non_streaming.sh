curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: DEV-API-KEY-12345678-ABCDEFGHIJKLMNOP" \
  -d '{
    "model": "llama3.2",
    "messages": [
      {"role": "user", "content": "What is machine learning?"}
    ],
    "stream": false,
    "options": {
      "index": "default"
    }
  }'