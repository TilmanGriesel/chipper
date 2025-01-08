import json
import logging
from typing import Generator

import requests
from core.model_exceptions import ModelNotFoundError


class OllamaModelManager:
    def __init__(self, ollama_url: str, allow_model_pull: bool):
        self.logger = logging.getLogger(__name__)
        self.ollama_url = ollama_url
        self.allow_model_pull = allow_model_pull

    def check_server_health(self):
        try:
            self.logger.info(
                f"Checking connectivity to Ollama server at {self.ollama_url}"
            )
            health_response = requests.get(self.ollama_url)

            if health_response.status_code != 200:
                raise Exception("Ollama server connectivity check failed.")

            self.logger.info("Successfully connected to the Ollama server")
        except requests.ConnectionError as e:
            self.logger.error(
                f"Connection error while checking Ollama server: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Error during Ollama server connectivity check: {str(e)}",
                exc_info=True,
            )
            raise

    def verify_and_pull_model(self, model_name: str) -> Generator[dict, None, None]:
        try:
            self.logger.info(f"Checking availability of model: {model_name}")
            yield {"type": "model_status", "status": "checking", "model": model_name}

            show_response = requests.post(
                f"{self.ollama_url}/api/show", json={"model": model_name}
            )

            if show_response.status_code == 200:
                yield {
                    "type": "model_status",
                    "status": "available",
                    "model": model_name,
                }
                self.logger.info(f"Model '{model_name}' is already available locally")
                return

            if not self.allow_model_pull:
                error_msg = (
                    f"Model '{model_name}' not found locally and auto-pull is disabled"
                )
                self.logger.error(error_msg)
                yield {
                    "type": "model_status",
                    "status": "error",
                    "model": model_name,
                    "error": error_msg,
                }
                raise ModelNotFoundError(error_msg)

            yield from self._pull_model(model_name)

        except ModelNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to verify or pull model {model_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            yield {
                "type": "model_status",
                "status": "error",
                "model": model_name,
                "error": error_msg,
            }
            raise

    def _pull_model(self, model_name: str) -> Generator[dict, None, None]:
        self.logger.info(f"Model '{model_name}' not found locally, initiating pull...")
        yield {"type": "model_status", "status": "pulling", "model": model_name}

        last_percentage = -1
        pull_successful = False

        with requests.post(
            f"{self.ollama_url}/api/pull", json={"model": model_name}, stream=True
        ) as response:
            if response.status_code != 200:
                error_msg = f"Model pull failed: {response.text}"
                self.logger.error(error_msg)
                yield {
                    "type": "model_status",
                    "status": "error",
                    "model": model_name,
                    "error": error_msg,
                }
                raise Exception(error_msg)

            for line in response.iter_lines():
                if line:
                    progress = json.loads(line)
                    if "total" in progress and "completed" in progress:
                        progress_raw = progress["completed"] / progress["total"]
                        current_percentage = int(progress_raw * 100)
                        if current_percentage > last_percentage:
                            yield {
                                "type": "model_status",
                                "status": "progress",
                                "model": model_name,
                                "percentage": current_percentage,
                            }
                            last_percentage = current_percentage
                            if current_percentage == 100:
                                pull_successful = True

        if pull_successful:
            yield {"type": "model_status", "status": "complete", "model": model_name}
            self.logger.info(f"Model '{model_name}' pulled successfully")
        else:
            error_msg = f"Model '{model_name}' not found after pull attempt"
            self.logger.error(error_msg)
            yield {
                "type": "model_status",
                "status": "error",
                "model": model_name,
                "error": error_msg,
            }
            raise Exception(error_msg)
