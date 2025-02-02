import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from haystack.dataclasses import ChatMessage, ChatRole


class ConversationLogger:
    def __init__(self, system_info: dict, log_dir: str = "conversation_logs"):
        """Initialize the conversation logger.

        Args:
            system_info: Dictionary containing system information to be logged
            log_dir: Directory where conversation logs will be stored
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.system_info = system_info

    def _serialize_chat_message(
        self, message: Union[ChatMessage, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Serialize a ChatMessage object or dict into a consistent dictionary format.

        Args:
            message: ChatMessage object or dictionary to serialize

        Returns:
            Dictionary representation of the message
        """
        try:
            if isinstance(message, ChatMessage):
                return {
                    "role": message.role.value
                    if isinstance(message.role, ChatRole)
                    else message.role,
                    "content": message.text,
                    "name": message.name,
                    "meta": message.meta,
                }
            elif isinstance(message, dict):
                if "llm" in message and "replies" in message["llm"]:
                    replies = message["llm"]["replies"]
                    if replies and isinstance(replies[0], ChatMessage):
                        return self._serialize_chat_message(replies[0])
                return message

            raise ValueError(f"Unsupported message type: {type(message)}")

        except Exception as e:
            return {
                "error": f"Serialization error: {str(e)}",
                "content": str(message),
                "type": str(type(message)),
            }

    def log_conversation(
        self,
        query: str,
        response: Union[ChatMessage, Dict[str, Any]],
        conversation: List[ChatMessage] = None,
    ) -> None:
        """Log a conversation exchange to a JSON file.

        Args:
            query: The user's query string
            response: Response containing LLM replies (either ChatMessage or dict)
            conversation: Optional list of previous messages in the conversation
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"conversation_{timestamp}.json"

        try:
            response_meta = {}
            if isinstance(response, dict) and "llm" in response:
                response_meta = response.get("llm", {}).get("meta", {})

            log_entry = {
                "timestamp": timestamp,
                "query": query,
                "system_info": self.system_info,
                "response": {
                    "llm": {
                        "replies": [self._serialize_chat_message(response)],
                        "meta": response_meta,
                    }
                },
                "previous_conversation": [
                    self._serialize_chat_message(msg) for msg in (conversation or [])
                ],
            }

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)

        except Exception as e:
            error_file = self.log_dir / f"error_{timestamp}.txt"
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(f"Error logging conversation: {str(e)}\n")
                f.write(f"Query: {query}\n")
                f.write(f"Response type: {type(response)}\n")
                f.write(f"Response: {str(response)}\n")
