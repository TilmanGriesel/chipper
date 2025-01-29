import json
import logging
import os
from typing import Optional

import requests
from flask import Response, request, stream_with_context

logger = logging.getLogger(__name__)


class OllamaProxy:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")

    def _proxy_request(self, path: str, method: str = "GET", stream: bool = False):
        url = f"{self.base_url}{path}"
        headers = {k: v for k, v in request.headers if k != "Host"}
        data = request.get_data() if method != "GET" else None

        try:
            response = requests.request(
                method=method, url=url, headers=headers, data=data, stream=stream
            )

            if stream:
                return self._handle_streaming_response(response)
            return self._handle_standard_response(response)

        except Exception as e:
            logger.error(f"Error proxying request to Ollama: {str(e)}")
            return Response(
                json.dumps({"error": str(e)}), status=500, mimetype="application/json"
            )

    def _handle_streaming_response(self, response):
        def generate():
            for chunk in response.iter_content(chunk_size=None):
                yield chunk

        return Response(
            stream_with_context(generate()),
            status=response.status_code,
            headers={
                "Content-Type": response.headers.get(
                    "Content-Type", "application/json"
                ),
                "Transfer-Encoding": "chunked",
            },
        )

    def _handle_standard_response(self, response):
        return Response(
            response.content,
            status=response.status_code,
            headers={
                "Content-Type": response.headers.get("Content-Type", "application/json")
            },
        )

    def generate(self):
        return self._proxy_request("/api/generate", "POST", stream=True)

    def tags(self):
        return self._proxy_request("/api/tags", "GET")

    def pull(self):
        return self._proxy_request("/api/pull", "POST", stream=True)
