"""Tests for backend/core/processors/base_loader.py"""
from unittest.mock import MagicMock

import numpy as np
import pytest

from backend.core.processors.base_loader import BaseDataLoader


# Minimal concrete subclass for testing
class ConcreteLoader(BaseDataLoader):
    def process_data(self, data_path):
        return np.zeros(384)

    def generate_query_embedding(self, query):
        return np.zeros(384)


@pytest.fixture
def loader():
    mock_db = MagicMock()
    mock_db.add_memory.return_value = "some-doc-id"
    return ConcreteLoader(mock_db)


# ---------------------------------------------------------------------------
# _generate_doc_id
# ---------------------------------------------------------------------------

def test_generate_doc_id_from_text_is_deterministic(loader):
    id1 = loader._generate_doc_id(text="hello")
    id2 = loader._generate_doc_id(text="hello")
    assert id1 == id2

def test_generate_doc_id_from_file_path_is_deterministic(loader):
    id1 = loader._generate_doc_id(file_path="/data/img.png")
    id2 = loader._generate_doc_id(file_path="/data/img.png")
    assert id1 == id2

def test_generate_doc_id_different_inputs_differ(loader):
    assert loader._generate_doc_id(text="a") != loader._generate_doc_id(text="b")

def test_generate_doc_id_raises_with_no_args(loader):
    with pytest.raises(ValueError):
        loader._generate_doc_id()


# ---------------------------------------------------------------------------
# save_memory — text
# ---------------------------------------------------------------------------

def test_save_memory_text_calls_add_memory(loader):
    embedding = np.zeros(384)
    metadata = {"type": "text", "text": "hello", "source": "file.txt"}
    loader.save_memory(embedding, metadata)
    loader.vector_db.add_memory.assert_called_once()

def test_save_memory_text_record_has_text_key(loader):
    embedding = np.zeros(384)
    metadata = {"type": "text", "text": "hello", "source": "file.txt"}
    loader.save_memory(embedding, metadata)
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["text"] == "hello"
    assert record["image"] is None

def test_save_memory_text_record_has_doc_id(loader):
    embedding = np.zeros(384)
    metadata = {"type": "text", "text": "hello", "source": "file.txt"}
    loader.save_memory(embedding, metadata)
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert "doc_id" in record
    assert record["doc_id"]  # not empty


# ---------------------------------------------------------------------------
# save_memory — image
# ---------------------------------------------------------------------------

def test_save_memory_image_record_has_image_key(loader):
    embedding = np.zeros(512)
    metadata = {"type": "image", "source": "/data/img.png"}
    loader.save_memory(embedding, metadata)
    record = loader.vector_db.add_memory.call_args[1]["record"]
    assert record["image"] == "/data/img.png"
    assert record["text"] is None

def test_save_memory_image_doc_id_based_on_source(loader):
    embedding = np.zeros(512)
    metadata = {"type": "image", "source": "/data/img.png"}
    loader.save_memory(embedding, metadata)
    record = loader.vector_db.add_memory.call_args[1]["record"]
    expected_id = loader._generate_doc_id(file_path="/data/img.png")
    assert record["doc_id"] == expected_id


# ---------------------------------------------------------------------------
# delete_all_memories
# ---------------------------------------------------------------------------

def test_delete_all_memories_calls_delete_for_each(loader):
    loader.vector_db.get_all_memories.return_value = [
        {"doc_id": "a"},
        {"doc_id": "b"},
    ]
    loader.delete_all_memories()
    assert loader.vector_db.delete_memory.call_count == 2
