import json
import logging
import os
from typing import Optional

import requests
from flask import Response, request, stream_with_context

logger = logging.getLogger(__name__)


class OllamaProxy:
    """
    A proxy class for interacting with the Ollama API.

    This class provides methods for all Ollama API endpoints, handling both streaming
    and non-streaming responses, and managing various model operations.
    Ref: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the OllamaProxy with a base URL.

        Args:
            base_url: The base URL for the Ollama API. Defaults to environment variable
                     OLLAMA_URL or 'http://localhost:11434'
        """
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")

    def _proxy_request(
        self, path: str, method: str = "GET", stream: bool = False
    ) -> Response:
        """
        Make a proxied request to the Ollama API.

        Args:
            path: The API endpoint path
            method: The HTTP method to use
            stream: Whether to stream the response

        Returns:
            A Flask Response object
        """
        url = f"{self.base_url}{path}"
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ["host", "transfer-encoding"]
        }

        data = request.get_data() if method != "GET" else None

        try:
            response = requests.request(
                method=method, url=url, headers=headers, data=data, stream=stream
            )

            if stream:
                return self._handle_streaming_response(response)
            return self._handle_standard_response(response)

        except Exception as e:
            logger.error(f"Error proxying request to Ollama: {str(e)}", exc_info=True)
            return Response(
                json.dumps({"error": "An internal error has occurred."}),
                status=500,
                mimetype="application/json",
            )

    def _handle_streaming_response(self, response: requests.Response) -> Response:
        """Handle streaming responses from the Ollama API."""

        def generate():
            try:
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk
            except Exception as e:
                logger.error(f"Error streaming response: {str(e)}", exc_info=True)
                yield json.dumps({"error": "An internal error has occurred."}).encode()

        response_headers = {
            "Content-Type": response.headers.get("Content-Type", "application/json")
        }

        return Response(
            stream_with_context(generate()),
            status=response.status_code,
            headers=response_headers,
        )

    def _handle_standard_response(self, response: requests.Response) -> Response:
        """Handle non-streaming responses from the Ollama API."""
        return Response(
            response.content,
            status=response.status_code,
            headers={
                "Content-Type": response.headers.get("Content-Type", "application/json")
            },
        )

    # Generation endpoints
    def generate(self) -> Response:
        """Generate a completion for a given prompt."""
        return self._proxy_request("/api/generate", "POST", stream=True)

    def chat(self) -> Response:
        """Generate the next message in a chat conversation."""
        return self._proxy_request("/api/chat", "POST", stream=True)

    def embeddings(self) -> Response:
        """Generate embeddings (legacy endpoint)."""
        return self._proxy_request("/api/embeddings", "POST")

    def embed(self) -> Response:
        """Generate embeddings from a model."""
        return self._proxy_request("/api/embed", "POST")

    # Model management endpoints
    def create(self) -> Response:
        """Create a model."""
        return self._proxy_request("/api/create", "POST", stream=True)

    def show(self) -> Response:
        """Show model information."""
        return self._proxy_request("/api/show", "POST")

    def copy(self) -> Response:
        """Copy a model."""
        return self._proxy_request("/api/copy", "POST")

    def delete(self) -> Response:
        """Delete a model."""
        return self._proxy_request("/api/delete", "DELETE")

    def pull(self) -> Response:
        """Pull a model from the Ollama library."""
        return self._proxy_request("/api/pull", "POST", stream=True)

    def push(self) -> Response:
        """Push a model to the Ollama library."""
        return self._proxy_request("/api/push", "POST", stream=True)

    # Blob management endpoints
    def check_blob(self, digest: str) -> Response:
        """Check if a blob exists."""
        return self._proxy_request(f"/api/blobs/{digest}", "HEAD")

    def push_blob(self, digest: str) -> Response:
        """Push a blob to the server."""
        return self._proxy_request(f"/api/blobs/{digest}", "POST")

    # Model listing and status endpoints
    def list_local_models(self) -> Response:
        """List models available locally."""
        return self._proxy_request("/api/tags", "GET")

    def list_running_models(self) -> Response:
        """List models currently loaded in memory."""
        return self._proxy_request("/api/ps", "GET")

    def version(self) -> Response:
        """Get the Ollama version."""
        return self._proxy_request("/api/version", "GET")
