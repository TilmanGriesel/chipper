import json
from datetime import datetime
from pathlib import Path
from typing import List


class ConversationLogger:
    def __init__(self, system_info: dict, log_dir: str = "conversation_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.system_info = system_info

    def log_conversation(
        self, query: str, response: dict, conversation: List[dict] = None
    ):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"conversation_{timestamp}.json"

        log_entry = {
            "timestamp": timestamp,
            "query": query,
            "system_info": self.system_info,
            "response": response.get("llm", {}).get("replies", []),
            "previous_conversation": conversation or [],
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
