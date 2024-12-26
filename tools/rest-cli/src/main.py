import argparse
import asyncio
import logging
import os
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List, Deque
from urllib.parse import urljoin

import aiohttp
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.theme import Theme


class MessageType(Enum):
    USER = "user"
    ASSISTANT = "chipper"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class Message:
    content: str
    type: MessageType
    timestamp: float = None


class APIError(Exception):
    pass


class Config:
    def __init__(
        self, base_url, api_key, timeout, verify_ssl, log_level, max_context_size
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.log_level = log_level
        self.max_context_size = max_context_size
        if not self.api_key:
            raise ValueError("API key must be provided.")


class AsyncAPIClient:
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "X-API-Key": self.config.api_key,
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(
                total=self.config.timeout,
                connect=30.0,
                sock_read=90.0,
                sock_connect=30.0,
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        url = urljoin(self.config.base_url, endpoint)
        kwargs.setdefault("ssl", self.config.verify_ssl)
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")

    async def query(
        self, query_text: str, conversation_context: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        return await self._make_request(
            "POST",
            "/api/query",
            json={"query": query_text, "conversation": conversation_context},
        )

    async def health_check(self) -> Dict[str, Any]:
        self.logger.info(f"Executing health check... {self.config.base_url}")
        return await self._make_request("GET", "/health")


class ChatInterface:
    def __init__(self, config: Config):
        self.config = config
        self.theme = Theme(
            {
                "user": "bold green",
                "chipper": "bold blue",
                "system": "bold blue",
                "error": "bold red",
            }
        )
        self.console = Console(theme=self.theme)
        self.conversation_context: Deque[Dict[str, str]] = deque(
            maxlen=self.config.max_context_size
        )
        self.message_history: List[Message] = []
        self.commands = {
            "/quit": self._cmd_quit,
            "/clear": self._cmd_clear,
            "/history": self._cmd_history,
            "/help": self._cmd_help,
            "/context": self._cmd_context,
        }

    def display_welcome(self):
        welcome_text = """
Available commands:
* /help    - Show this help message
* /quit    - Exit the application
* /clear   - Clear the screen
* /history - Show message history
* /context - Adjust context size

Type your message and press Enter to chat.
"""
        self.console.print(
            Panel(Markdown(welcome_text), title="Chipper CLI Chat", border_style="blue")
        )

    def display_message(self, message: Message):
        panel = Panel(
            Markdown(message.content),
            border_style=message.type.value,
            title=message.type.value.title(),
            title_align="left",
        )
        self.console.print(panel)
        self.message_history.append(message)
        if message.type in [MessageType.USER, MessageType.ASSISTANT]:
            self.conversation_context.append(
                {"role": message.type.value, "content": message.content}
            )

    def get_user_input(self) -> str:
        return Prompt.ask("\n[bold green]You[/bold green]")

    async def _cmd_quit(self) -> bool:
        self.console.print("[blue]Goodbye![/blue]")
        return False

    async def _cmd_clear(self) -> bool:
        self.console.clear()
        self.display_welcome()
        return True

    async def _cmd_history(self) -> bool:
        if not self.message_history:
            self.console.print("[blue]No message history available.[/blue]")
            return True
        for msg in self.message_history[-10:]:
            self.console.print(f"[{msg.type.value}]{msg.content}[/{msg.type.value}]")
        return True

    async def _cmd_help(self) -> bool:
        self.display_welcome()
        return True

    async def _cmd_context(self) -> bool:
        new_size = IntPrompt.ask(
            "[blue]Enter new context size[/blue]", default=self.config.max_context_size
        )
        self.conversation_context = deque(
            list(self.conversation_context), maxlen=new_size
        )
        self.config.max_context_size = new_size
        self.console.print(f"[blue]Context size updated to {new_size}[/blue]")
        return True

    async def process_command(self, command: str) -> bool:
        cmd_func = self.commands.get(command.lower())
        if cmd_func:
            return await cmd_func()
        self.console.print(f"[blue]Unknown command: {command}[/blue]")
        return True

    async def run(self):
        try:
            async with AsyncAPIClient(self.config) as client:
                health_status = await client.health_check()
                if health_status.get("status") != "healthy":
                    raise APIError("API is not healthy")
                self.display_welcome()
                while True:
                    user_input = self.get_user_input()
                    if user_input.startswith("/"):
                        should_continue = await self.process_command(user_input)
                        if not should_continue:
                            break
                        continue
                    user_message = Message(user_input, MessageType.USER)
                    self.display_message(user_message)
                    try:
                        with self.console.status(
                            "[bold blue]Thinking...", spinner="dots"
                        ):
                            response = await client.query(
                                user_input, list(self.conversation_context)
                            )
                            replies = (
                                response.get("result", {})
                                .get("llm", {})
                                .get("replies", ["No response received"])
                            )
                        for reply in replies:
                            assistant_message = Message(reply, MessageType.ASSISTANT)
                            self.display_message(assistant_message)
                    except APIError as e:
                        error_message = Message(f"Error: {str(e)}", MessageType.ERROR)
                        self.display_message(error_message)
        except Exception as e:
            self.console.print(f"[red]Fatal error: {str(e)}[/red]")


def setup_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


def main():
    parser = argparse.ArgumentParser(description="Chipper CLI Chat Application")
    parser.add_argument(
        "--host", default=os.getenv("WEB_API_HOST", "0.0.0.0"), help="API Host"
    )
    parser.add_argument(
        "--port", default=os.getenv("WEB_API_PORT", "8000"), help="API Port"
    )
    parser.add_argument("--api_key", default=os.getenv("WEB_API_KEY"), help="API Key")
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("API_TIMEOUT", "120")),
        help="API Timeout",
    )
    parser.add_argument(
        "--verify_ssl",
        action="store_true",
        default=os.getenv("WEB_REQUIRE_SECURE", "False").lower() == "true",
        help="Verify SSL",
    )
    parser.add_argument(
        "--log_level", default=os.getenv("LOG_LEVEL", "INFO"), help="Log Level"
    )
    parser.add_argument(
        "--max_context_size",
        type=int,
        default=int(os.getenv("MAX_CONTEXT_SIZE", "10")),
        help="Maximum Context Size",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    config = Config(
        base_url,
        args.api_key,
        args.timeout,
        args.verify_ssl,
        args.log_level,
        args.max_context_size,
    )

    setup_logging(config.log_level)
    chat = ChatInterface(config)
    asyncio.run(chat.run())


if __name__ == "__main__":
    main()
