import logging
import os
from pathlib import Path
from typing import List, Set

from cli import parse_args
from core.document_processor import DocumentProcessor
from core.embedder import RAGEmbedder
from haystack import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("APP_VERSION", "[DEV]")
BUILD_NUMBER = os.getenv("APP_BUILD_NUM", "0")


def load_blacklist(base_path: str) -> Set[str]:
    blacklist_file = Path(base_path) / ".ragignore"
    default_blacklist = set()

    if blacklist_file.exists():
        try:
            with open(blacklist_file, "r") as f:
                custom_blacklist = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }
            logger.info(f"Loaded custom blacklist from .ragignore: {custom_blacklist}")
            return default_blacklist.union(custom_blacklist)
        except Exception as e:
            logger.warning(
                f"Error reading .ragignore file: {e}. Using default blacklist."
            )
            return default_blacklist
    else:
        logger.info("No .ragignore file found. Using default blacklist.")
        return default_blacklist


def log_args(args):
    logger.info("Configuration:")
    config_dict = {
        "Elasticsearch URL": args.es_url,
        "Ollama URL": args.ollama_url,
        "Embedding Model": args.embedding_model,
        "Document Path": args.path or "Not specified",
        "File Extensions": ", ".join(args.extensions),
        "Debug Mode": args.debug,
    }

    for key, value in config_dict.items():
        logger.info(f"{key}: {value}")


def process_documents(args) -> List[Document]:
    logger.info("Starting document processing")
    blacklist = load_blacklist("./")
    processor = DocumentProcessor(
        base_path=args.path,
        file_extensions=args.extensions,
        blacklist=blacklist,
        split_by=args.split_by,
        split_length=args.split_length,
        split_overlap=args.split_overlap,
        split_threshold=args.split_threshold,
    )
    documents = processor.process_files()
    logger.info(f"Processed {len(documents)} documents")
    return documents


def main():
    args = parse_args()
    log_args(args)

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    try:
        logger.info("Initializing RAG Embedder")
        embedder = RAGEmbedder(
            provider_name=args.provider,
            es_url=args.es_url,
            es_index=args.es_index,
            ollama_url=args.ollama_url,
            embedding_model=args.embedding_model,
        )
        logger.debug("RAG Embedder initialized successfully")

        if not args.path:
            logger.fatal("No path provided")
            exit(1)

        documents = process_documents(args)

        if documents:
            logger.info("Starting document embedding")
            embedder.embed_documents(documents)
            logger.info(f"Successfully embedded {len(documents)} documents")
            embedder.finalize()
        else:
            logger.warning("No documents to embed")

        if args.stats:
            logger.info("Retrieving pipeline statistics")
            embedder_stats = embedder.metrics_tracker.metrics
            logger.info(f"Embedder Metrics: {embedder_stats}")

    except Exception:
        logger.error("Error in pipeline execution", exc_info=True)
        raise


def show_welcome():
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    print("\n", flush=True)
    print(f"{RED}", flush=True)
    print("        __    _                      ", flush=True)
    print("  _____/ /_  (_)___  ____  ___  _____", flush=True)
    print(" / ___/ __ \\/ / __ \\/ __ \\/ _ \\/ ___/", flush=True)
    print("/ /__/ / / / / /_/ / /_/ /  __/ /    ", flush=True)
    print("\\___/_/ /_/_/ .___/ .___/\\___/_/     ", flush=True)
    print("           /_/   /_/                 ", flush=True)
    print(f"{RESET}", flush=True)
    print(f"{YELLOW}       Chipper Embed {APP_VERSION}.{BUILD_NUMBER}", flush=True)
    print(f"{RESET}\n", flush=True)


if __name__ == "__main__":
    show_welcome()
    logger.info("Starting RAG Embedding...")
    main()
