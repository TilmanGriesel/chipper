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

    def _print_tree(self, tree: Dict, prefix: str = "", is_last: bool = True) -> List[str]:
        if tree is None:
            return []

        tree_lines = []
        items = list(tree.items() if isinstance(tree, dict) else [])

        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            tree_lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}")

            if isinstance(subtree, dict):
                extension = "    " if is_last_item else "│   "
                subtree_lines = self._print_tree(
                    subtree, prefix + extension, is_last_item
                )
                tree_lines.extend(subtree_lines)

        return tree_lines