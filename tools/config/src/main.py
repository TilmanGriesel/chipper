#!/usr/bin/env python3
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.style import Style
from rich.table import Table
from rich.text import Text

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False)],
)
logger = logging.getLogger("env_manager")


@dataclass
class EnvVariable:
    key: str
    value: str
    description: Optional[str] = None
    var_type: str = "string"


@dataclass
class EnvFile:
    path: Path
    service: str
    index: int
    relative_depth: int


@dataclass
class EnvManagerConfig:
    debug: bool = False
    start_path: Path = Path(".")
    env_patterns: List[str] = field(default_factory=lambda: ["*.env*"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.example"])
    show_full_path: bool = False
    blocklist_paths: List[str] = field(default_factory=lambda: [])


class EnvManager:
    def __init__(self, config: Optional[EnvManagerConfig] = None):
        self.console = Console(force_terminal=True, width=120)
        self.config = config or EnvManagerConfig()
        if self.config.debug:
            logger.setLevel(logging.DEBUG)

        self.styles = {
            "header": Style(color="bright_white", bold=True),
            "key": Style(color="cyan", bold=True),
            "value": Style(color="green"),
            "type": Style(color="yellow"),
            "description": Style(color="bright_black"),
            "prompt": Style(color="bright_magenta", bold=True),
            "error": Style(color="red", bold=True),
            "success": Style(color="bright_green", bold=True),
        }

    def parse_type(self, value: str) -> Tuple[str, str]:
        if value.lower() in ("true", "false"):
            return "bool", value.lower()
        try:
            float(value)
            return ("float", value) if "." in value else ("int", value)
        except ValueError:
            return "string", value

    def parse_env_file(self, file_path: Path) -> Dict[str, EnvVariable]:
        env_vars: Dict[str, EnvVariable] = {}
        pending_comments: List[str] = []

        for line in file_path.read_text().splitlines():
            line = line.strip()
            if not line:
                pending_comments = []
                continue

            if line.startswith("#"):
                if not re.match(r"^#\s*[A-Za-z_][A-Za-z0-9_]*=", line):
                    comment = line[1:].strip()
                    if comment:  # Only add non-empty comments
                        pending_comments.append(comment)
                continue

            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
            if match:
                key, value = match.groups()
                value = value.strip('"').strip("'")
                var_type, processed_value = self.parse_type(value)

                description = None
                if pending_comments:
                    description = "\n".join(pending_comments)

                env_vars[key] = EnvVariable(
                    key=key,
                    value=processed_value,
                    description=description,
                    var_type=var_type,
                )
                pending_comments = []

        return env_vars

    def is_blocklisted(self, path: Path) -> bool:
        try:
            relative_path = path.relative_to(self.config.start_path)
            path_str = str(relative_path).replace("\\", "/")

            for blocklist_pattern in self.config.blocklist_paths:
                pattern = blocklist_pattern.replace("\\", "/")

                if (
                    path_str == pattern
                    or path_str.startswith(f"{pattern}/")
                    or f"/{pattern}/" in f"/{path_str}/"
                ):
                    return True
            return False
        except ValueError:
            return False

    def find_env_files(self) -> List[Path]:
        env_files = []
        for pattern in self.config.env_patterns:
            for path in self.config.start_path.rglob(pattern):
                if (
                    path.is_file()
                    and not any(path.match(exc) for exc in self.config.exclude_patterns)
                    and not self.is_blocklisted(path)
                ):
                    env_files.append(path)
        return sorted(env_files)

    def categorize_env_files(self, env_files: List[Path]) -> List[EnvFile]:
        categorized_files = []
        start_path = self.config.start_path.resolve()

        for idx, file_path in enumerate(env_files, 1):
            service = file_path.parent.name
            relative_depth = len(file_path.resolve().relative_to(start_path).parts) - 1

            categorized_files.append(
                EnvFile(
                    path=file_path,
                    service=service,
                    index=idx,
                    relative_depth=relative_depth,
                )
            )

        return sorted(categorized_files, key=lambda x: (x.path.name))

    def display_env_files(self, env_files: List[EnvFile]) -> None:
        table = Table(
            show_header=True,
            header_style=self.styles["header"],
            box=box.ROUNDED,
            show_edge=False,
            padding=(0, 1),
        )

        table.add_column(
            "#", style="bright_blue", justify="center", width=4, no_wrap=True
        )
        table.add_column("Service", style="bright_yellow", width=20, no_wrap=True)
        if self.config.show_full_path:
            table.add_column("Path", style="bright_white", overflow="fold")

        current_service = None
        for env_file in env_files:
            if current_service != env_file.service:
                if current_service is not None:
                    if self.config.show_full_path:
                        table.add_row("", "", "", style="dim")
                    else:
                        table.add_row("", "", style="dim")
                current_service = env_file.service

            relative_path = env_file.path.relative_to(self.config.start_path)
            if self.config.show_full_path:
                table.add_row(
                    str(env_file.index),
                    Text(env_file.service.capitalize(), style=self.styles["key"]),
                    Text(str(relative_path), style=self.styles["value"]),
                )
            else:
                table.add_row(
                    str(env_file.index),
                    Text(env_file.service.capitalize(), style=self.styles["key"]),
                )

        self.console.print("\n")
        self.console.print(
            Panel(
                table,
                title="[bold]Environment Configuration Files[/bold]",
                border_style="bright_blue",
                padding=(0, 0),
            )
        )

    def prompt_value(self, var: EnvVariable) -> Optional[str]:
        self.console.print("\n")
        panel = Panel(
            f"Type: [yellow]{var.var_type}[/yellow]\nCurrent: [green]{var.value}[/green]",
            title=f"[bold cyan]{var.key}[/bold cyan]",
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(panel)

        try:
            if var.var_type == "bool":
                value = str(
                    Confirm.ask(
                        Text("New value", style=self.styles["prompt"]),
                        default=var.value.lower() == "true",
                    )
                ).lower()
            else:
                value = Prompt.ask(
                    Text("New value", style=self.styles["prompt"]),
                    default=var.value,
                    show_default=False,
                )
                if value == var.value:
                    return None
        except KeyboardInterrupt:
            return None

        try:
            if var.var_type == "int":
                int(value)
            elif var.var_type == "float":
                float(value)
            return value
        except ValueError:
            if var.var_type in ("int", "float"):
                self.console.print(
                    Text(f"Invalid {var.var_type}", style=self.styles["error"])
                )
                return self.prompt_value(var)
        return value

    def display_vars(self, env_vars: Dict[str, EnvVariable], file_path: Path) -> None:
        table = Table(
            show_header=True,
            header_style=self.styles["header"],
            box=box.ROUNDED,
            expand=True,
            show_edge=False,
            padding=(1, 1),
        )

        table.add_column(
            "#", style="bright_blue", justify="center", width=4, no_wrap=True
        )
        table.add_column("Key", style=self.styles["key"], overflow="fold")
        table.add_column("Value", style=self.styles["value"], overflow="fold")
        table.add_column(
            "Type", style=self.styles["type"], justify="center", width=8, no_wrap=True
        )
        table.add_column(
            "Description", style=self.styles["description"], overflow="fold"
        )

        for idx, var in enumerate(env_vars.values(), 1):
            table.add_row(
                str(idx),
                var.key,
                var.value,
                var.var_type,
                var.description or "",
            )

        self.console.print("\n")
        self.console.print(
            Panel(
                table,
                title=f"[bold]{file_path.name}[/bold]",
                subtitle=f"[dim]{file_path.parent}[/dim]",
                border_style="bright_blue",
                padding=(1, 0),
            )
        )

    def save_env_file(self, file_path: Path, env_vars: Dict[str, EnvVariable]) -> None:
        content = file_path.read_text()
        for key, var in env_vars.items():
            pattern = f"^{re.escape(key)}\\s*=\\s*[^\n]*$"
            replacement = f"{key}={var.value}"

            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        file_path.write_text(content)

        self.console.print("\n")
        self.console.print(
            Panel(
                Text("✓ Changes saved successfully", style=self.styles["success"]),
                border_style="bright_green",
                padding=(1, 2),
            )
        )

    def run(self) -> None:
        try:
            while True:
                raw_env_files = self.find_env_files()

                if not raw_env_files:
                    raise FileNotFoundError("No .env files found")

                env_files = self.categorize_env_files(raw_env_files)
                self.display_env_files(env_files)

                selection = Prompt.ask(
                    Text("\nSelect file to edit", style=self.styles["prompt"]),
                    default="1",
                    show_default=True,
                )

                if selection == "0":
                    break

                try:
                    selection = int(selection)
                    if not 1 <= selection <= len(env_files):
                        raise ValueError()
                except ValueError:
                    self.console.print(
                        Text("Invalid selection", style=self.styles["error"])
                    )
                    continue

                selected_file = next(f.path for f in env_files if f.index == selection)
                env_vars = self.parse_env_file(selected_file)
                modified = False

                while True:
                    var_keys = list(env_vars.keys())
                    self.display_vars(env_vars, selected_file)

                    try:
                        var_selection = Prompt.ask(
                            Text(
                                "\nVariable to edit (0 to finish)",
                                style=self.styles["prompt"],
                            ),
                            default="0",
                        )

                        if var_selection == "0":
                            break

                        var_selection = int(var_selection)
                        if not 1 <= var_selection <= len(var_keys):
                            raise ValueError()

                        selected_key = var_keys[var_selection - 1]
                        selected_var = env_vars[selected_key]
                        new_value = self.prompt_value(selected_var)
                        if new_value is not None:
                            env_vars[selected_key].value = new_value
                            modified = True
                    except ValueError:
                        self.console.print(
                            Text("Invalid selection", style=self.styles["error"])
                        )

                if modified and Confirm.ask(
                    Text("\nSave changes?", style=self.styles["prompt"])
                ):
                    self.save_env_file(selected_file, env_vars)
                    self.display_vars(env_vars, selected_file)
                else:
                    self.console.print(
                        Panel(
                            Text("Changes discarded", style="yellow"),
                            border_style="yellow",
                            padding=(1, 2),
                        )
                    )

        except KeyboardInterrupt:
            self.console.print("\n")
            self.console.print(
                Panel(
                    Text("Operation cancelled", style="yellow"),
                    border_style="yellow",
                    padding=(1, 2),
                )
            )
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise


def main():
    blocklist = os.getenv("ENV_MANAGER_BLOCKLIST", "").split(",")
    config = EnvManagerConfig(
        debug=os.getenv("ENV_MANAGER_DEBUG", "").lower() == "true",
        show_full_path=os.getenv("ENV_MANAGER_SHOW_PATH", "").lower() == "true",
        blocklist_paths=[p for p in blocklist if p]
        if blocklist
        else EnvManagerConfig.blocklist_paths.default_factory(),
    )

    manager = EnvManager(config)
    manager.run()


if __name__ == "__main__":
    main()
