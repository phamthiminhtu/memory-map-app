"""
Bulk-ingest images into the vector DB.

Incremental & idempotent: for each image in --images-dir, computes the same
doc_id BaseDataLoader would generate (sha256 of the file path) and skips the
image if that doc_id already exists in the DB. Only images that are new since
the last run get embedded and written. Safe to re-run any time (e.g. after
dropping new files into data/images/) without re-processing or duplicating
existing memories.

Usage:
    # from the repo root, with the project venv active
    python scripts/bulk_ingest_image.py
    python scripts/bulk_ingest_image.py --images-dir data/images --persist-dir data/chroma_image
    python scripts/bulk_ingest_image.py --dry-run
"""

import argparse
import hashlib
import logging
import sys
from pathlib import Path

# Make the repo root importable (`db`, `etl`) when this script is run directly.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.chroma_db import ChromaDB
from etl.data_loaders.image_loader import ImageDataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bulk_ingest_image")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


def compute_doc_id(image_path: str) -> str:
    """
    Mirrors BaseDataLoader._generate_doc_id(file_path=...): sha256 of the file
    path string. Computing it up front lets us check for an existing memory
    before paying for image loading + embedding.
    """
    return hashlib.sha256(image_path.encode("utf-8")).hexdigest()


def find_images(images_dir: Path):
    """All image files directly inside images_dir, sorted for stable, predictable runs."""
    return sorted(
        p for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def already_ingested(vector_db: ChromaDB, doc_id: str) -> bool:
    return vector_db.get_memory(doc_id) is not None


def bulk_ingest_images(images_dir: str, persist_dir: str, dry_run: bool = False) -> dict:
    images_dir_path = Path(images_dir)
    if not images_dir_path.is_dir():
        raise FileNotFoundError(f"Images directory not found: {images_dir_path}")

    vector_db = ChromaDB(persist_directory=persist_dir)
    loader = ImageDataLoader(vector_db)

    stats = {"found": 0, "ingested": 0, "skipped": 0, "failed": 0}

    for image_path in find_images(images_dir_path):
        stats["found"] += 1
        path_str = str(image_path)
        doc_id = compute_doc_id(path_str)

        if already_ingested(vector_db, doc_id):
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
        "Done. found=%d ingested=%d skipped=%d failed=%d"
        % (stats["found"], stats["ingested"], stats["skipped"], stats["failed"])
    )
    return stats


def parse_args():
    parser = argparse.ArgumentParser(
        description="Incrementally ingest new images from a folder into ChromaDB."
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
        "--dry-run", action="store_true",
        help="List what would be ingested/skipped without writing to the DB",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    bulk_ingest_images(args.images_dir, args.persist_dir, dry_run=args.dry_run)
