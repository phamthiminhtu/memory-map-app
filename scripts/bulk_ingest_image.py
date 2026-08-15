"""
Bulk-ingest images and/or text files into the vector DB.

Incremental & idempotent by default: skips files already in the DB.
Use --full-refresh to wipe the target DB and re-ingest everything.

Usage:
    python scripts/bulk_ingest_image.py --type image
    python scripts/bulk_ingest_image.py --type text
    python scripts/bulk_ingest_image.py --type all
    python scripts/bulk_ingest_image.py --type image --full-refresh
    python scripts/bulk_ingest_image.py --dry-run
"""

import argparse
import hashlib
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.db.chroma_db import ChromaDB
from backend.core.processors.image_loader import ImageDataLoader
from backend.core.processors.text_loader import TextDataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bulk_ingest")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
TEXT_EXTENSIONS = {".txt", ".md"}


def compute_image_doc_id(image_path: str) -> str:
    """Mirrors BaseDataLoader._generate_doc_id(file_path=...): sha256 of the file path."""
    return hashlib.sha256(image_path.encode("utf-8")).hexdigest()


def compute_text_doc_id(text_content: str) -> str:
    """Mirrors BaseDataLoader._generate_doc_id(text=...): sha256 of the text content."""
    return hashlib.sha256(text_content.encode("utf-8")).hexdigest()


def find_files(directory: Path, extensions: set):
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in extensions)


def already_ingested(vector_db: ChromaDB, doc_id: str) -> bool:
    return vector_db.get_memory(doc_id) is not None


def bulk_ingest_images(images_dir: str, persist_dir: str, full_refresh: bool = False, dry_run: bool = False) -> dict:
    images_dir_path = Path(images_dir)
    if not images_dir_path.is_dir():
        raise FileNotFoundError(f"Images directory not found: {images_dir_path}")

    vector_db = ChromaDB(persist_directory=persist_dir)

    if full_refresh and not dry_run:
        logger.info("Full refresh: resetting image DB")
        vector_db.reset()

    loader = ImageDataLoader(vector_db)
    stats = {"found": 0, "ingested": 0, "skipped": 0, "failed": 0}

    for image_path in find_files(images_dir_path, IMAGE_EXTENSIONS):
        stats["found"] += 1
        path_str = str(image_path)
        doc_id = compute_image_doc_id(path_str)

        if not full_refresh and already_ingested(vector_db, doc_id):
            logger.info(f"Skipping (already ingested): {image_path.name}")
            stats["skipped"] += 1
            continue

        if dry_run:
            logger.info(f"[dry-run] Would ingest: {image_path.name} (doc_id={doc_id})")
            stats["ingested"] += 1
            continue

        try:
            metadata = {"title": image_path.stem, "filename": image_path.name}
            loader.save_image_memory(path_str, metadata=metadata)
            logger.info(f"Ingested: {image_path.name} (doc_id={doc_id})")
            stats["ingested"] += 1
        except Exception as e:
            logger.error(f"Failed to ingest {image_path.name}: {e}")
            stats["failed"] += 1

    logger.info(
        "[image] Done. found=%d ingested=%d skipped=%d failed=%d"
        % (stats["found"], stats["ingested"], stats["skipped"], stats["failed"])
    )
    return stats


def bulk_ingest_texts(texts_dir: str, persist_dir: str, full_refresh: bool = False, dry_run: bool = False) -> dict:
    texts_dir_path = Path(texts_dir)
    if not texts_dir_path.is_dir():
        raise FileNotFoundError(f"Texts directory not found: {texts_dir_path}")

    vector_db = ChromaDB(persist_directory=persist_dir)

    if full_refresh and not dry_run:
        logger.info("Full refresh: resetting text DB")
        vector_db.reset()

    loader = TextDataLoader(vector_db)
    stats = {"found": 0, "ingested": 0, "skipped": 0, "failed": 0}

    for text_path in find_files(texts_dir_path, TEXT_EXTENSIONS):
        stats["found"] += 1
        path_str = str(text_path)

        try:
            content = text_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read {text_path.name}: {e}")
            stats["failed"] += 1
            continue

        doc_id = compute_text_doc_id(content)

        if not full_refresh and already_ingested(vector_db, doc_id):
            logger.info(f"Skipping (already ingested): {text_path.name}")
            stats["skipped"] += 1
            continue

        if dry_run:
            logger.info(f"[dry-run] Would ingest: {text_path.name} (doc_id={doc_id})")
            stats["ingested"] += 1
            continue

        try:
            metadata = {"title": text_path.stem, "filename": text_path.name, "date": text_path.stem}
            loader.save_text_memory(text_path=path_str, metadata=metadata)
            logger.info(f"Ingested: {text_path.name} (doc_id={doc_id})")
            stats["ingested"] += 1
        except Exception as e:
            logger.error(f"Failed to ingest {text_path.name}: {e}")
            stats["failed"] += 1

    logger.info(
        "[text] Done. found=%d ingested=%d skipped=%d failed=%d"
        % (stats["found"], stats["ingested"], stats["skipped"], stats["failed"])
    )
    return stats


def parse_args():
    parser = argparse.ArgumentParser(
        description="Incrementally ingest new images and/or text files into ChromaDB."
    )
    parser.add_argument(
        "--type", choices=["image", "text", "all"], default="image",
        help="What to ingest (default: image)",
    )
    parser.add_argument(
        "--images-dir", default="data/images",
        help="Folder of images to ingest (default: data/images)",
    )
    parser.add_argument(
        "--persist-dir", default="data/chroma_image",
        help="ChromaDB persist directory for image memories (default: data/chroma_image)",
    )
    parser.add_argument(
        "--texts-dir", default="data/text",
        help="Folder of text files to ingest (default: data/text)",
    )
    parser.add_argument(
        "--text-persist-dir", default="data/chroma_text",
        help="ChromaDB persist directory for text memories (default: data/chroma_text)",
    )
    parser.add_argument(
        "--full-refresh", action="store_true",
        help="Wipe the target DB and re-ingest all files (per type)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List what would be ingested/skipped without writing to the DB",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.type in ("image", "all"):
        bulk_ingest_images(args.images_dir, args.persist_dir, full_refresh=args.full_refresh, dry_run=args.dry_run)
    if args.type in ("text", "all"):
        bulk_ingest_texts(args.texts_dir, args.text_persist_dir, full_refresh=args.full_refresh, dry_run=args.dry_run)
