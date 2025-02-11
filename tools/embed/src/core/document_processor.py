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
        self.blacklist = blacklist or set()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(log_level)

        # Log initialization configuration
        config = {
            "base_path": str(self.base_path),
            "file_extensions": self.file_extensions,
            "blacklist": sorted(self.blacklist),
            "split_by": split_by,
            "split_length": split_length,
            "split_overlap": split_overlap,
            "split_threshold": split_threshold,
        }
        self.logger.info(
            "Document processor configuration: %s", json.dumps(config, indent=None)
        )

        self.document_store = InMemoryDocumentStore()
        self.converter = TextFileToDocument(store_full_path=False)
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
        tree = {}
        for file in sorted(files):
            relative_path = file.relative_to(self.base_path)
            parts = list(relative_path.parts)

            # Navigate/create the tree structure
            current = tree
            for part in parts[:-1]:  # Process all but the last part (directories)
                if part not in current:
                    current[part] = {}
                current = current[part]
                if current is None:  # Safety check
                    current = {}

            # Add the file as a leaf node
            if parts:  # Safety check
                current[parts[-1]] = None

        return tree

    def _print_tree(
        self, tree: Dict, prefix: str = "", is_last: bool = True
    ) -> List[str]:
        if tree is None:
            return []

        tree_lines = []
        items = list(tree.items() if isinstance(tree, dict) else [])

        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            icon = "└── " if is_last_item else "├── "
            tree_lines.append(f"{prefix}{icon}{name}")

            if isinstance(subtree, dict):
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
                "Blacklisted path: %s (matched: %s)", path, blacklisted_parts
            )
        return is_blacklisted

    def _log_processing_summary(self, stats: ProcessingStats):
        """Log a summary of the processing results."""
        summary_lines = [
            "Processing Summary:",
            f"Files Processed: {stats.processed_files}",
            f"Total Documents: {stats.total_documents}",
            f"Split Documents: {stats.split_documents}",
            f"Failed Files: {stats.failed_files}",
            f"Skipped Files: {stats.skipped_files}",
            f"Blacklisted Files: {stats.blacklisted_files}",
        ]

        if stats.total_file_size > 0:
            size_mb = stats.total_file_size / (1024 * 1024)
            summary_lines.append(f"Total File Size: {size_mb:.2f} MB")

        for line in summary_lines:
            self.logger.info(line)

    def process_files(self):
        stats = ProcessingStats()
        self.logger.info(
            "Starting document processing from base path: %s", self.base_path
        )
        self.logger.info("Active blacklist patterns: %s", sorted(self.blacklist))

        if not self.base_path.exists():
            self.logger.error("Base path not found: %s", self.base_path)
            return []

        self.logger.info("Starting file search...")

        files = []
        blacklisted_files = []
        blacklist_stats = {}
        current_directory = None

        for idx, ext in enumerate(self.file_extensions, 1):
            self.logger.info(
                "Searching [%d/%d]: *%s", idx, len(self.file_extensions), ext
            )
            try:
                found_files = list(self.base_path.rglob(f"*{ext}"))
                current_found = len(found_files)
                if current_found > 0:
                    self.logger.info(
                        "Found %d files with extension %s", current_found, ext
                    )

                valid_files = []
                blacklist_details = defaultdict(list)  # Track blacklist reasons

                for file in found_files:
                    # Show directory changes for better context
                    file_dir = file.parent
                    if file_dir != current_directory:
                        current_directory = file_dir
                        if self.logger.level <= logging.DEBUG:
                            self.logger.debug(
                                "Scanning: %s", file_dir.relative_to(self.base_path)
                            )

                    if self._is_blacklisted(file):
                        blacklist_reason = next(
                            part for part in file.parts if part in self.blacklist
                        )
                        blacklist_details[blacklist_reason].append(file)
                        blacklist_stats[blacklist_reason] = (
                            blacklist_stats.get(blacklist_reason, 0) + 1
                        )
                        stats.blacklisted_files += 1
                        blacklisted_files.append(file)
                    else:
                        valid_files.append(file)

                if blacklist_details:
                    self.logger.info("Blacklisted files:")
                    for reason, blacklisted in blacklist_details.items():
                        self.logger.info(
                            "  %d files in '%s' directories", len(blacklisted), reason
                        )
                        if self.logger.level <= logging.DEBUG:
                            for bf in blacklisted[:5]:
                                self.logger.debug(
                                    "    - %s", bf.relative_to(self.base_path)
                                )
                            if len(blacklisted) > 5:
                                self.logger.debug(
                                    "    ... and %d more", len(blacklisted) - 5
                                )

                files.extend(valid_files)

            except Exception as e:
                self.logger.error("Error searching for %s files: %s", ext, str(e))
                continue

        total_files = len(files)
        self.logger.info("Summary: Found %d files to process", total_files)

        if blacklist_stats:
            self.logger.info("Blacklist summary:")
            for pattern, count in sorted(
                blacklist_stats.items(), key=lambda x: x[1], reverse=True
            ):
                self.logger.info("  %d files skipped due to '%s'", count, pattern)

        if files:
            self.logger.info("Files to be processed:")
            tree = self._build_tree_structure(files)
            tree_output = self._print_tree(tree)
            self.logger.info(".")  # root
            for line in tree_output:
                self.logger.info(line)

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
                self.logger.error("Error processing files: %s", str(e), exc_info=True)
                return []
