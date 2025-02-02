import json
import queue
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import elasticsearch
from api.config import DEBUG, logger
from core.pipeline_config import QueryPipelineConfig
from core.rag_pipeline import RAGQueryPipeline
from flask import Response, jsonify, stream_with_context


def format_stream_response(
    config: QueryPipelineConfig,
    content: str = "",
    done: bool = False,
    done_reason: Optional[str] = None,
    images: Optional[List[str]] = None,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    **metrics,
) -> Dict[str, Any]:
    """Format streaming response according to Ollama-API specification."""
    response = {
        "model": config.model_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "done": done,
    }

    if not done:
        message = {"role": "assistant", "content": content}
        if images:
            message["images"] = images
        if tool_calls:
            message["tool_calls"] = tool_calls
        response["message"] = message
    else:
        if done_reason:
            response["done_reason"] = done_reason

        if done_reason == "error":
            response["message"] = {"role": "assistant", "content": content}

        response.update(
            {
                "total_duration": metrics.get("total_duration", 0),
                "load_duration": metrics.get("load_duration", 0),
                "prompt_eval_count": metrics.get("prompt_eval_count", 0),
                "prompt_eval_duration": metrics.get("prompt_eval_duration", 0),
                "eval_count": metrics.get("eval_count", 0),
                "eval_duration": metrics.get("eval_duration", 0),
            }
        )

    return response


def format_model_status(
    status: Dict[str, Any], config: QueryPipelineConfig
) -> Optional[Dict[str, Any]]:
    """Format model status updates for streaming response."""
    model = status.get("model", "unknown")
    status_type = status.get("status")

    if status_type == "pulling":
        content = f"Starting to download model {model}..."
    elif status_type == "progress":
        percentage = status.get("percentage", 0)
        content = f"Downloading model {model}: `{percentage}%` complete"
    elif status_type == "complete":
        content = f"Successfully downloaded model {model}"
    elif status_type == "error" and "pull" in status.get("error", "").lower():
        error_msg = status.get("error", "Unknown error")
        content = f"Error downloading model {model}: {error_msg}"
    else:
        return None

    content += "\n"
    return format_stream_response(config, content=content)


def handle_streaming_response(
    config: QueryPipelineConfig,
    query: str,
    conversation: List[Dict[str, str]],
    format_schema: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Response:
    q = queue.Queue()
    start_time = time.time_ns()
    prompt_start = None

    def streaming_callback(chunk):
        nonlocal prompt_start
        if prompt_start is None:
            prompt_start = time.time_ns()

        if chunk.content:
            if format_schema and chunk.is_final:
                try:
                    content = json.loads(chunk.content)
                    response_data = format_stream_response(
                        config, json.dumps(content), done=True, done_reason="stop"
                    )
                except json.JSONDecodeError:
                    response_data = format_stream_response(
                        config,
                        "Error: Failed to generate valid JSON response.",
                        done=True,
                        done_reason="error",
                    )
            else:
                response_data = format_stream_response(
                    config,
                    chunk.content,
                    images=getattr(chunk, "images", None),
                    tool_calls=getattr(chunk, "tool_calls", None),
                )

            q.put(json.dumps(response_data) + "\n")

    rag = RAGQueryPipeline(config=config, streaming_callback=streaming_callback)

    def run_rag():
        try:
            # Track model loading
            load_start = time.time_ns()
            for status in rag.initialize_and_check_models():
                # Handle model pull status
                if status_data := format_model_status(status, config):
                    q.put(json.dumps(status_data) + "\n")

                if status.get("status") == "error":
                    error_data = format_stream_response(
                        config,
                        f"Error: Model initialization failed - {status.get('error')}",
                        done=True,
                        done_reason="error",
                    )
                    q.put(json.dumps(error_data) + "\n")
                    return

            load_duration = time.time_ns() - load_start

            response_text = rag.run_query(
                query=query, conversation=conversation, print_response=DEBUG
            )

            # Calculate final metrics
            end_time = time.time_ns()
            final_data = format_stream_response(
                config,
                done=True,
                done_reason="stop",
                total_duration=end_time - start_time,
                load_duration=load_duration,
                prompt_eval_count=len(conversation) + 1,
                prompt_eval_duration=end_time - (prompt_start or start_time),
                eval_count=len(response_text.split())
                if response_text is not None
                else 0,
                eval_duration=end_time - (prompt_start or start_time),
            )
            q.put(json.dumps(final_data) + "\n")

        except elasticsearch.BadRequestError as e:
            error_data = format_stream_response(
                config,
                content=f"Error: Embedding retriever error - {str(e)}",
                done=True,
                done_reason="error",
            )
            q.put(json.dumps(error_data) + "\n")

        except Exception as e:
            error_data = format_stream_response(
                config, content=f"Error: {str(e)}", done=True, done_reason="error"
            )
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            q.put(json.dumps(error_data) + "\n")

    thread = threading.Thread(target=run_rag, daemon=True)
    thread.start()

    def generate():
        while True:
            try:
                data = q.get(timeout=120)
                if data:
                    yield data

                if '"done": true' in data:
                    logger.info("Streaming completed.")
                    break

            except queue.Empty:
                # Send an empty object for heartbeat
                yield json.dumps({}) + "\n"
                logger.warning("Queue timeout. Sending heartbeat.")
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_data = format_stream_response(
                    config, "Streaming error occurred.", done=True, done_reason="error"
                )
                yield json.dumps(error_data) + "\n"
                break

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def handle_standard_response(
    config: QueryPipelineConfig,
    query: str,
    conversation: List[Dict[str, str]],
    format_schema: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Response:
    start_time = time.time_ns()
    rag = RAGQueryPipeline(config=config)

    try:
        # Track model loading time
        load_start = time.time_ns()
        for status in rag.initialize_and_check_models():
            if status.get("status") == "error":
                raise Exception(f"Model initialization failed: {status.get('error')}")
        load_duration = time.time_ns() - load_start

        # Track query execution time
        prompt_start = time.time_ns()
        result = rag.run_query(
            query=query, conversation=conversation, print_response=False
        )
        end_time = time.time_ns()

        if result and "llm" in result and "replies" in result["llm"]:
            response_content = result["llm"]["replies"][0]

            # Handle structured output if format_schema is provided
            if format_schema:
                try:
                    content = json.loads(response_content)
                    response_content = json.dumps(content)
                except json.JSONDecodeError:
                    raise Exception("Failed to generate valid JSON response")

            eval_count = len(response_content.split()) if response_content else 0

            response = {
                "model": config.model_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "message": {"role": "assistant", "content": response_content},
                "done": True,
                "done_reason": "stop",
                "total_duration": end_time - start_time,
                "load_duration": load_duration,
                "prompt_eval_count": len(conversation) + 1,
                "prompt_eval_duration": end_time - prompt_start,
                "eval_count": eval_count,
                "eval_duration": end_time - prompt_start,
            }

            return jsonify(response)

    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
        error_response = {
            "model": config.model_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "done": True,
            "done_reason": "error",
            "error": str(e),
        }
        return jsonify(error_response)
