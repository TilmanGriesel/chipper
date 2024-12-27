curl -v -N http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: DEMO-API-KEY-123" \
  -d '{
    "query": "Write me a long story about a dog called Chipper.",
    "conversation": []
  }'
  