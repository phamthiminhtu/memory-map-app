"""Tests for backend/core/processors/text_loader.py — mocks SentenceTransformer."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from backend.core.processors.text_loader import TextDataLoader


@pytest.fixture
def loader():
    mock_db = MagicMock()
    mock_db.add_memory.return_value = "doc-id"
    with patch("backend.core.processors.text_loader.SentenceTransformer") as mock_st:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.ones((1, 384))
        mock_st.return_value = mock_model
        yield TextDataLoader(mock_db)


# ---------------------------------------------------------------------------
# load_text
# ---------------------------------------------------------------------------

def test_load_text_from_string(loader):
    assert loader.load_text(text="hello") == "hello"

def test_load_text_from_file(loader, tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("diary entry")
    assert loader.load_text(text_path=str(f)) == "diary entry"

def test_load_text_raises_with_no_args(loader):
    with pytest.raises(ValueError):
        loader.load_text()


# ---------------------------------------------------------------------------
# process_data
# ---------------------------------------------------------------------------

def test_process_data_returns_1d_array(loader):
    result = loader.process_data("some text")
    assert isinstance(result, np.ndarray)
    assert result.ndim == 1


# ---------------------------------------------------------------------------
# save_text_memory
# ---------------------------------------------------------------------------

def test_save_text_memory_sets_type_text(loader):
    loader.save_text_memory(text="hello")
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["metadata"]["type"] == "text"

def test_save_text_memory_stores_text_in_metadata(loader):
    loader.save_text_memory(text="my diary")
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["metadata"]["text"] == "my diary"

def test_save_text_memory_adds_timestamp_when_no_date(loader):
    loader.save_text_memory(text="hello")
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert "timestamp" in record["metadata"]

def test_save_text_memory_no_timestamp_when_date_given(loader):
    loader.save_text_memory(text="hello", metadata={"date": "2026-07-14"})
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert "timestamp" not in record["metadata"]
    assert record["metadata"]["date"] == "2026-07-14"

def test_save_text_memory_text_key_in_record(loader):
    loader.save_text_memory(text="hello world")
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["text"] == "hello world"
    assert record["image"] is None
