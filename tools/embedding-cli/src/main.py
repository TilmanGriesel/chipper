import logging
from pathlib import Path
from typing import List, Set

from haystack import Document
from core.embedder import RAGEmbedder
from cli import parse_args
from core.document_processor import DocumentProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    blacklist = load_blacklist(args.path)
    processor = DocumentProcessor(
        base_path=args.path, file_extensions=args.extensions, blacklist=blacklist
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

    except Exception as e:
        logger.error("Error in pipeline execution", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("Starting RAG Embedding...")
    main()
