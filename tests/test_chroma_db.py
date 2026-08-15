"""Tests for backend/db/chroma_db.py — contract of add/get/search/delete."""
import numpy as np
import pytest

from backend.db.chroma_db import ChromaDB


@pytest.fixture
def db(tmp_path):
    return ChromaDB(persist_directory=str(tmp_path / "chroma"))


def _text_record(text="hello world", doc_id=None):
    embedding = np.random.rand(384).tolist()
    doc_id = doc_id or "doc-text-1"
    return {
        "doc_id": doc_id,
        "text": text,
        "image": None,
        "embedding": embedding,
        "metadata": {"type": "text", "text": text, "date": "2026-07-14"},
    }


def _image_record(source="img.png", doc_id="doc-img-1"):
    embedding = np.random.rand(512).tolist()
    return {
        "doc_id": doc_id,
        "text": None,
        "image": source,
        "embedding": embedding,
        "metadata": {"type": "image", "source": source, "date": "2026-07-14"},
    }


# ---------------------------------------------------------------------------
# add_memory
# ---------------------------------------------------------------------------

def test_add_memory_returns_doc_id(db):
    record = _text_record()
    returned_id = db.add_memory(record)
    assert returned_id == record["doc_id"]

def test_add_memory_text_is_retrievable(db):
    record = _text_record()
    db.add_memory(record)
    result = db.get_memory(record["doc_id"])
    assert result is not None
    assert result["doc_id"] == record["doc_id"]

def test_add_memory_image_stored_without_text(db):
    record = _image_record()
    db.add_memory(record)
    result = db.get_memory(record["doc_id"])
    assert result is not None
    assert result["text"] == "" or result["text"] is None

def test_add_memory_metadata_roundtrips(db):
    record = _text_record()
    db.add_memory(record)
    result = db.get_memory(record["doc_id"])
    assert result["metadata"]["date"] == "2026-07-14"
    assert result["metadata"]["type"] == "text"


# ---------------------------------------------------------------------------
# get_memory
# ---------------------------------------------------------------------------

def test_get_memory_missing_returns_none(db):
    assert db.get_memory("nonexistent-id") is None

def test_get_memory_returns_correct_record(db):
    r1 = _text_record(text="first", doc_id="id-1")
    r2 = _text_record(text="second", doc_id="id-2")
    db.add_memory(r1)
    db.add_memory(r2)
    result = db.get_memory("id-1")
    assert "first" in result["text"]


# ---------------------------------------------------------------------------
# get_all_memories
# ---------------------------------------------------------------------------

def test_get_all_memories_empty(db):
    assert db.get_all_memories() == []

def test_get_all_memories_returns_all(db):
    db.add_memory(_text_record(doc_id="a"))
    db.add_memory(_text_record(doc_id="b"))
    all_memories = db.get_all_memories()
    assert len(all_memories) == 2
    ids = {m["doc_id"] for m in all_memories}
    assert ids == {"a", "b"}


# ---------------------------------------------------------------------------
# delete_memory
# ---------------------------------------------------------------------------

def test_delete_memory_removes_record(db):
    record = _text_record()
    db.add_memory(record)
    db.delete_memory(record["doc_id"])
    assert db.get_memory(record["doc_id"]) is None

def test_delete_memory_returns_true_on_success(db):
    record = _text_record()
    db.add_memory(record)
    assert db.delete_memory(record["doc_id"]) is True


# ---------------------------------------------------------------------------
# search_memories
# ---------------------------------------------------------------------------

def test_search_memories_returns_list(db):
    db.add_memory(_text_record())
    embedding = np.random.rand(384)

    def query_fn(query):
        return embedding

    results = db.search_memories("hello", query_fn, n_results=1)
    assert isinstance(results, list)
    assert len(results) == 1

def test_search_memories_result_has_required_keys(db):
    db.add_memory(_text_record())
    embedding = np.random.rand(384)

    results = db.search_memories("hello", lambda q: embedding, n_results=1)
    result = results[0]
    assert "doc_id" in result
    assert "text" in result
    assert "distance" in result
    assert "metadata" in result

def test_search_memories_respects_n_results(db):
    for i in range(5):
        db.add_memory(_text_record(doc_id=f"doc-{i}"))
    embedding = np.random.rand(384)
    results = db.search_memories("hello", lambda q: embedding, n_results=2)
    assert len(results) == 2


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------

def test_reset_clears_all_memories(db):
    db.add_memory(_text_record(doc_id="a"))
    db.add_memory(_text_record(doc_id="b"))
    db.reset()
    assert db.get_all_memories() == []
