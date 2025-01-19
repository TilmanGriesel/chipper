import argparse
import os

from dotenv import load_dotenv

load_dotenv()

APP_VERSION = os.getenv("APP_VERSION", "[DEV]")
BUILD_NUMBER = os.getenv("APP_BUILD_NUM", "0")


def parse_args():
    parser = argparse.ArgumentParser(
        description=f"Chipper Embed CLI {APP_VERSION}.{BUILD_NUMBER}"
    )

    parser.add_argument(
        "--path",
        type=str,
        default="/app/data",
        help="Base path to process documents from",
    )

    parser.add_argument(
        "--extensions",
        type=str,
        nargs="+",
        default=[
            # Text files
            ".txt",
            ".md",
            ".rst",
            ".log",
            ".csv",
            ".json",
            ".yaml",
            ".yml",
            # Web development
            ".html",
            ".htm",
            ".css",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".php",
            # Python
            ".py",
            ".pyx",
            ".pyi",
            ".ipynb",
            # C/C++
            ".c",
            ".cpp",
            ".cc",
            ".cxx",
            ".h",
            ".hpp",
            ".hxx",
            # Java/Kotlin
            ".java",
            ".kt",
            ".gradle",
            # C#
            ".cs",
            ".csproj",
            ".cshtml",
            # Ruby
            ".rb",
            ".erb",
            ".rake",
            # Shell scripts
            ".sh",
            ".bash",
            ".zsh",
            # Windows scripts
            ".bat",
            ".cmd",
            ".ps1",
            ".vbs",
            ".vbe",
            ".js",
            ".jse",
            ".wsf",
            ".wsh",
            # Apple scripts
            ".scpt",
            ".scptd",
            ".applescript",
            # Configuration files
            ".xml",
            ".ini",
            ".conf",
            ".cfg",
            ".toml",
            # QML/Qt
            ".qml",
            ".ui",
            # Rust
            ".rs",
            # Go
            ".go",
            # Swift
            ".swift",
        ],
        help="List of file extensions to process",
    )

    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug logging"
    )

    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["ollama", "hf"],
        help="Embedding provider",
    )

    # Service Configuration
    parser.add_argument(
        "--es-url",
        type=str,
        default=os.getenv("ES_URL", "http://localhost:9200"),
        help="URL for the Elasticsearch service",
    )

    parser.add_argument(
        "--es-index",
        type=str,
        default=os.getenv("ES_INDEX", "default"),
        help="Index for the Elasticsearch service",
    )

    parser.add_argument(
        "--es-basic-auth-user",
        type=str,
        default=os.getenv("ES_BASIC_AUTH_USERNAME", ""),
        help="Username for the Elasticsearch service authentication",
    )

    parser.add_argument(
        "--es-basic-auth-password",
        type=str,
        default=os.getenv("ES_BASIC_AUTH_PASSWORD", ""),
        help="Password for the Elasticsearch service authentication",
    )

    parser.add_argument(
        "--ollama-url",
        type=str,
        default=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        help="URL for the Ollama service",
    )

    # Model Configuration

    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        help="Model to use for embeddings",
    )

    # Text Splitting Configuration
    parser.add_argument(
        "--split-by",
        type=str,
        default="word",
        choices=["word", "sentence", "passage", "page", "line"],
        help="Method to split text documents",
    )

    parser.add_argument(
        "--split-length",
        type=int,
        default=200,
        help="Number of units per split",
    )

    parser.add_argument(
        "--split-overlap",
        type=int,
        default=20,
        help="Number of units to overlap between splits",
    )

    parser.add_argument(
        "--split-threshold",
        type=int,
        default=5,
        help="Minimum length of split to keep",
    )

    # Misc
    parser.add_argument(
        "--stats", action="store_true", default=False, help="Enable statistics logging"
    )

    args = parser.parse_args()

    return args
