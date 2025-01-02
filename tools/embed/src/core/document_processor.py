import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from haystack import Pipeline
from haystack.components.converters.txt import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.document_stores.types import DuplicatePolicy


@dataclass
class ProcessingStats:
    processed_files: int = 0
    total_documents: int = 0
    failed_files: int = 0
    total_processing_time: float = 0
    skipped_files: int = 0
    total_file_size: int = 0
    split_documents: int = 0
    blacklisted_files: int = 0


class DocumentProcessor:
    def __init__(
        self,
        base_path: str,
        file_extensions: List[str],
        blacklist: Set[str] = None,
        split_by: str = "word",
        split_length: int = 200,
        split_overlap: int = 20,
        split_threshold: int = 5,
        log_level: int = logging.INFO,
    ):
        self.base_path = Path(base_path)
        self.file_extensions = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in file_extensions
        ]
        self.blacklist = blacklist or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(log_level)

        config = {
            "base_path": str(self.base_path),
            "file_extensions": self.file_extensions,
            "blacklist": sorted(self.blacklist),
            "split_by": split_by,
            "split_length": split_length,
            "split_overlap": split_overlap,
            "split_threshold": split_threshold,
        }
        self.logger.info(f"Initialized with config: {json.dumps(config, indent=2)}")

        self.document_store = InMemoryDocumentStore()
        self.converter = TextFileToDocument(
            store_full_path=False,
        )
        self.cleaner = DocumentCleaner(
            ascii_only=True,
            remove_empty_lines=True,
            remove_extra_whitespaces=True,
        )
        self.splitter = DocumentSplitter(
            split_by=split_by,
            split_length=split_length,
            split_overlap=split_overlap,
            split_threshold=split_threshold,
        )
        self.writer = DocumentWriter(
            document_store=self.document_store, policy=DuplicatePolicy.OVERWRITE
        )

        self.indexing_pipeline = Pipeline()
        self.indexing_pipeline.add_component(instance=self.converter, name="converter")
        self.indexing_pipeline.add_component(instance=self.cleaner, name="cleaner")
        self.indexing_pipeline.add_component(instance=self.splitter, name="splitter")
        self.indexing_pipeline.add_component(instance=self.writer, name="writer")

        self.indexing_pipeline.connect("converter.documents", "cleaner.documents")
        self.indexing_pipeline.connect("cleaner.documents", "splitter.documents")
        self.indexing_pipeline.connect("splitter.documents", "writer.documents")

    def _build_tree_structure(self, files: List[Path]) -> Dict:
        tree = defaultdict(list)
        for file in sorted(files):
            relative_path = file.relative_to(self.base_path)
            parts = list(relative_path.parts)
            current_dict = tree
            for i, part in enumerate(parts[:-1]):
                if part not in current_dict:
                    current_dict[part] = defaultdict(list)
                current_dict = current_dict[part]
            current_dict[parts[-1]] = None
        return tree

    def _print_tree(
        self, tree: Dict, prefix: str = "", is_last: bool = True
    ) -> List[str]:
        tree_lines = []
        items = list(tree.items())

        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")

            if subtree is not None:
                extension = "    " if is_last_item else "│   "
                subtree_lines = self._print_tree(
                    subtree, prefix + extension, is_last_item
                )
                tree_lines.extend(subtree_lines)

        return tree_lines

    def _is_blacklisted(self, path: Path) -> bool:
        blacklisted_parts = [part for part in path.parts if part in self.blacklist]
        is_blacklisted = len(blacklisted_parts) > 0

        if is_blacklisted:
            self.logger.debug(
                f"Blacklisted path: {path} (matched: {blacklisted_parts})"
            )
        return is_blacklisted

    def process_files(self):
        stats = ProcessingStats()

        self.logger.info(
            f"Starting document processing from base path: {self.base_path}"
        )
        self.logger.info(f"File extensions to process: {self.file_extensions}")
        self.logger.info(f"Active blacklist patterns: {sorted(self.blacklist)}")

        if not self.base_path.exists():
            self.logger.error(f"Base path not found: {self.base_path}")
            return []

        files = []
        blacklisted_files = []
        blacklist_stats = {}

        for ext in self.file_extensions:
            found_files = list(self.base_path.rglob(f"*{ext}"))
            valid_files = []

            for file in found_files:
                if self._is_blacklisted(file):
                    blacklisted_part = next(
                        part for part in file.parts if part in self.blacklist
                    )
                    blacklist_stats[blacklisted_part] = (
                        blacklist_stats.get(blacklisted_part, 0) + 1
                    )
                    stats.blacklisted_files += 1
                    blacklisted_files.append(file)
                else:
                    valid_files.append(file)

            files.extend(valid_files)

        total_files = len(files)
        self.logger.info(f"Found {total_files} files to process")

        if files:
            self.logger.info("\nFiles to be processed:")
            tree = self._build_tree_structure(files)
            tree_output = self._print_tree(tree)
            self.logger.info(".")  # root
            for line in tree_output:
                self.logger.info(line)

        if blacklist_stats:
            self.logger.info("\nBlacklist statistics:")
            for pattern, count in sorted(blacklist_stats.items()):
                self.logger.info(f"  - '{pattern}' matched {count} files")

        if not files:
            return []

        try:
            for file_path in files:
                stats.total_file_size += file_path.stat().st_size

            self.indexing_pipeline.run(
                {
                    "converter": {
                        "sources": files,
                        "meta": {
                            "processed_at": datetime.now().isoformat(),
                        },
                    }
                }
            )

            stats.processed_files = len(files)
            stats.total_documents = len(self.document_store.filter_documents())
            stats.split_documents = stats.total_documents

            self._log_processing_summary(stats)

            return self.document_store.filter_documents()

        except Exception as e:
            stats.failed_files += 1
            self.logger.error(f"Error processing files: {str(e)}", exc_info=True)
            return []

    def _log_processing_summary(self, stats: ProcessingStats) -> None:
        summary = f"""
Document processing summary:
------------------------
Files processed successfully: {stats.processed_files}
Files blacklisted: {stats.blacklisted_files}
Total documents after splitting: {stats.total_documents}
Total data processed: {stats.total_file_size / 1024 / 1024:.2f} MB
------------------------"""

        self.logger.info(summary)

        if stats.failed_files > 0:
            self.logger.warning(
                f"Failed to process {stats.failed_files} files. "
                "Check the log for detailed error messages."
            )
        if stats.skipped_files > 0:
            self.logger.debug(
                f"Skipped {stats.skipped_files} files (blacklisted: {stats.blacklisted_files}, "
                f"other: {stats.skipped_files - stats.blacklisted_files})"
            )


if __name__ == "__main__":
    processor = DocumentProcessor(
        base_path="",
        file_extensions=[".txt", ".md"],
        blacklist={"build", "node_modules", "dist", "out", "venv"},
        split_by="sentence",
        split_length=1,
    )
    documents = processor.process_files()
