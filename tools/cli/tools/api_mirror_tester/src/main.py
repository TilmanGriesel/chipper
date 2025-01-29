import asyncio
import json
from dataclasses import dataclass
from typing import Dict, List, Optional

import aiohttp


@dataclass
class EndpointConfig:
    path: str
    method: str
    sample_payload: Optional[Dict] = None


@dataclass
class ApiResponse:
    status: int
    headers: Dict
    body: Dict


@dataclass
class ComparisonResult:
    endpoint: str
    method: str
    match_score: float
    differences: List[str]
    Chipper_response: Optional[ApiResponse] = None
    ollama_response: Optional[ApiResponse] = None
    error: Optional[str] = None


class ApiMirrorTester:
    def __init__(
        self,
        Chipper_api_base: str,
        ollama_api_base: str = "http://localhost:11434",
        verify_ssl: bool = True,
    ):
        self.Chipper_api_base = Chipper_api_base.rstrip("/")
        self.ollama_api_base = ollama_api_base.rstrip("/")
        self.verify_ssl = verify_ssl

        self.endpoints = [
            EndpointConfig(
                path="/api/generate",
                method="POST",
                sample_payload={
                    "model": "llama2",
                    "prompt": "Why is the sky blue?",
                    "stream": False,
                },
            ),
            EndpointConfig(
                path="/api/chat",
                method="POST",
                sample_payload={
                    "model": "llama2",
                    "messages": [
                        {"role": "user", "content": "What is the capital of France?"}
                    ],
                    "stream": True,
                },
            ),
            EndpointConfig(path="/api/tags", method="GET"),
            EndpointConfig(
                path="/api/pull", method="POST", sample_payload={"name": "llama2"}
            ),
        ]

    async def test_endpoint(
        self, base_url: str, endpoint: EndpointConfig
    ) -> ApiResponse:
        """Test a single endpoint and return its response."""
        print(f"\nTesting {base_url}{endpoint.path}...")
        url = f"{base_url}{endpoint.path}"
        headers = (
            {"Content-Type": "application/json"} if endpoint.sample_payload else {}
        )

        connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.request(
                method=endpoint.method,
                url=url,
                json=endpoint.sample_payload,
                headers=headers,
            ) as response:
                if endpoint.path == "/api/chat" and endpoint.sample_payload.get(
                    "stream", False
                ):
                    print(f"Reading streaming response from {base_url}...")
                    chunks = []
                    chunk_count = 0
                    async for line in response.content:
                        if line:
                            chunk = line.decode().strip()
                            if chunk:
                                try:
                                    parsed_chunk = json.loads(chunk)
                                    chunks.append(parsed_chunk)
                                    chunk_count += 1
                                    if chunk_count % 5 == 0:
                                        print(
                                            f"Received {chunk_count} chunks from {base_url}..."
                                        )
                                except json.JSONDecodeError:
                                    print(
                                        f"Warning: Skipping invalid JSON chunk from {base_url}: {chunk[:100]}..."
                                    )

                    body = chunks[-1] if chunks else {}
                    print(
                        f"Completed streaming for {base_url}. Received {chunk_count} total chunks."
                    )
                else:
                    body = await response.json()

                return ApiResponse(
                    status=response.status, headers=dict(response.headers), body=body
                )

    def compare_responses(
        self, Chipper_response: ApiResponse, ollama_response: ApiResponse
    ) -> tuple[float, List[str]]:
        match_score = 0
        differences = []

        if Chipper_response.status == ollama_response.status:
            match_score += 0.25
        else:
            differences.append(
                f"Status code mismatch: {Chipper_response.status} vs {ollama_response.status}"
            )

        Chipper_content_type = Chipper_response.headers.get("content-type", "")
        ollama_content_type = ollama_response.headers.get("content-type", "")

        if Chipper_content_type == ollama_content_type:
            match_score += 0.25
        else:
            differences.append(
                f"Content-Type header mismatch: {Chipper_content_type} vs {ollama_content_type}"
            )

        Chipper_keys = set(Chipper_response.body.keys())
        ollama_keys = set(ollama_response.body.keys())

        common_keys = Chipper_keys & ollama_keys
        structure_score = len(common_keys) / max(len(Chipper_keys), len(ollama_keys))
        match_score += structure_score * 0.5

        missing_keys = ollama_keys - Chipper_keys
        extra_keys = Chipper_keys - ollama_keys

        if missing_keys:
            differences.append(f"Missing fields: {', '.join(missing_keys)}")
        if extra_keys:
            differences.append(f"Extra fields: {', '.join(extra_keys)}")

        return round(match_score, 2), differences

    async def compare_apis(self) -> List[ComparisonResult]:
        """Compare Chipper API against the Ollama API for all endpoints."""
        print("\nStarting API comparison...")
        total_endpoints = len(self.endpoints)
        results = []

        for idx, endpoint in enumerate(self.endpoints, 1):
            print(
                f"\nTesting endpoint {idx}/{total_endpoints}: {endpoint.method} {endpoint.path}"
            )
            try:
                print("\nTesting Chipper API endpoint...")
                Chipper_response = await self.test_endpoint(
                    self.Chipper_api_base, endpoint
                )

                print("\nTesting Ollama API endpoint...")
                ollama_response = await self.test_endpoint(
                    self.ollama_api_base, endpoint
                )

                match_score, differences = self.compare_responses(
                    Chipper_response, ollama_response
                )

                results.append(
                    ComparisonResult(
                        endpoint=endpoint.path,
                        method=endpoint.method,
                        match_score=match_score,
                        differences=differences,
                        Chipper_response=Chipper_response,
                        ollama_response=ollama_response,
                    )
                )
            except Exception as e:
                results.append(
                    ComparisonResult(
                        endpoint=endpoint.path,
                        method=endpoint.method,
                        match_score=0.0,
                        differences=[],
                        error=str(e),
                    )
                )

        return results

    def print_results(self, results: List[ComparisonResult]):
        """Print the comparison results in a readable format."""
        print("\nAPI Comparison Results:")
        print("=" * 80)

        for result in results:
            print(f"\nEndpoint: {result.method} {result.endpoint}")
            print("-" * 40)

            if result.error:
                print(f"Error: {result.error}")
                continue

            print(f"Match Score: {result.match_score * 100}%")

            if result.differences:
                print("\nDifferences found:")
                for diff in result.differences:
                    print(f"- {diff}")
            else:
                print("\nNo differences found!")


async def main():
    tester = ApiMirrorTester(
        Chipper_api_base="http://localhost:21434/",
        ollama_api_base="http://localhost:11434",
        verify_ssl=False,
    )

    results = await tester.compare_apis()
    tester.print_results(results)


if __name__ == "__main__":
    asyncio.run(main())
