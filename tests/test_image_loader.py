"""Tests for backend/core/processors/image_loader.py — mocks CLIP."""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from backend.core.processors.image_loader import ImageDataLoader


@pytest.fixture
def loader():
    mock_db = MagicMock()
    mock_db.add_memory.return_value = "doc-id"
    with patch("backend.core.processors.image_loader.clip") as mock_clip:
        mock_model = MagicMock()
        mock_model.encode_image.return_value = MagicMock(
            squeeze=lambda: MagicMock(numpy=lambda: np.random.rand(512))
        )
        mock_model.encode_text.return_value = MagicMock(
            squeeze=lambda: MagicMock(numpy=lambda: np.random.rand(512))
        )
        mock_clip.load.return_value = (mock_model, MagicMock())
        mock_clip.tokenize.return_value = MagicMock()
        yield ImageDataLoader(mock_db)


# ---------------------------------------------------------------------------
# _parse_filename_metadata (static — no loader needed)
# ---------------------------------------------------------------------------

def test_parse_filename_metadata_full_pattern():
    result = ImageDataLoader._parse_filename_metadata("data/2026-07-14_hiking_ridge_trail.png")
    assert result["date"] == "2026-07-14"
    assert result["description"] == "hiking ridge trail"

def test_parse_filename_metadata_date_only():
    result = ImageDataLoader._parse_filename_metadata("data/2026-07-14.png")
    assert result["date"] == "2026-07-14"
    assert "description" not in result

def test_parse_filename_metadata_no_match_returns_empty():
    result = ImageDataLoader._parse_filename_metadata("data/random_photo.png")
    assert result == {}

def test_parse_filename_metadata_uuid_returns_empty():
    result = ImageDataLoader._parse_filename_metadata(
        "data/E5C324FA-C6A7-4127-A40E-4C03510C0471.jpeg"
    )
    assert result == {}


# ---------------------------------------------------------------------------
# _combine_embeddings
# ---------------------------------------------------------------------------

def test_combine_embeddings_returns_normalized_vector(loader):
    img = np.random.rand(512)
    img /= np.linalg.norm(img)
    txt = np.random.rand(512)
    txt /= np.linalg.norm(txt)
    result = loader._combine_embeddings(img, txt)
    assert result.shape == (512,)
    assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-5)

def test_combine_embeddings_alpha_zero_equals_text(loader):
    img = np.zeros(512)
    txt = np.ones(512)
    txt /= np.linalg.norm(txt)
    result = loader._combine_embeddings(img, txt, alpha=0.0)
    assert np.allclose(result, txt, atol=1e-5)

def test_combine_embeddings_dimension_mismatch_raises(loader):
    img = np.random.rand(512)
    txt = np.random.rand(384)  # wrong dim
    with pytest.raises(ValueError):
        loader._combine_embeddings(img, txt)


# ---------------------------------------------------------------------------
# save_image_memory — metadata contract
# ---------------------------------------------------------------------------

def test_save_image_memory_parses_date_from_filename(loader, tmp_path):
    img_path = tmp_path / "2026-07-14_hiking.png"
    img_path.write_bytes(b"fake")

    with patch.object(loader, "process_data", return_value=np.zeros(512)):
        loader.save_image_memory(str(img_path))

    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["metadata"]["date"] == "2026-07-14"

def test_save_image_memory_stores_description_as_text(loader, tmp_path):
    img_path = tmp_path / "2026-07-14_hiking_ridge_trail.png"
    img_path.write_bytes(b"fake")

    with patch.object(loader, "process_data", return_value=np.zeros(512)):
        loader.save_image_memory(str(img_path))

    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["metadata"].get("text") == "hiking ridge trail"

def test_save_image_memory_sets_type_image(loader, tmp_path):
    img_path = tmp_path / "photo.png"
    img_path.write_bytes(b"fake")

    with patch.object(loader, "process_data", return_value=np.zeros(512)):
        loader.save_image_memory(str(img_path))

    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["metadata"]["type"] == "image"

def test_save_image_memory_image_key_in_record(loader, tmp_path):
    img_path = tmp_path / "photo.png"
    img_path.write_bytes(b"fake")

    with patch.object(loader, "process_data", return_value=np.zeros(512)):
        loader.save_image_memory(str(img_path))

    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["image"] is not None
    assert record["text"] is None
