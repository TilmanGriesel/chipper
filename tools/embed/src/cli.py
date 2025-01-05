import argparse
import os

from dotenv import load_dotenv

load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process documents with text embeddings and query capability",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
            ".txt",
            ".md",
            ".py",
            ".html",
            ".js",
            ".cpp",
            ".hpp",
            ".qml",
            ".xml",
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
