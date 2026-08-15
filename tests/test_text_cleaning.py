"""Tests for backend/utils/text_cleaning.py"""
from datetime import date

import pytest

from backend.utils.text_cleaning import (
    clean_text,
    extract_date_range,
    rerank_by_date,
    split_into_chunks,
)
from backend.utils.constants.text_parsing import DATE_BOOST_FACTOR


# ---------------------------------------------------------------------------
# clean_text
# ---------------------------------------------------------------------------

def test_clean_text_collapses_whitespace():
    assert clean_text("hello   world") == "hello world"

def test_clean_text_removes_special_chars():
    assert clean_text("hello, world!") == "hello world"

def test_clean_text_strips_leading_trailing():
    assert clean_text("  hello  ") == "hello"

def test_clean_text_empty():
    assert clean_text("") == ""


# ---------------------------------------------------------------------------
# split_into_chunks
# ---------------------------------------------------------------------------

def test_split_into_chunks_short_text_is_single_chunk():
    result = split_into_chunks("hello world", chunk_size=1000)
    assert result == ["hello world"]

def test_split_into_chunks_splits_on_size():
    # 10 words of ~5 chars each = ~60 chars; chunk_size=20 should produce multiple
    text = " ".join(["hello"] * 10)
    chunks = split_into_chunks(text, chunk_size=20)
    assert len(chunks) > 1

def test_split_into_chunks_reassemble_equals_original():
    text = " ".join(["word"] * 50)
    chunks = split_into_chunks(text, chunk_size=30)
    assert " ".join(chunks) == text


# ---------------------------------------------------------------------------
# extract_date_range
# ---------------------------------------------------------------------------

def test_extract_date_range_single_date():
    result = extract_date_range("What did I do on July 14, 2026?")
    assert result == (date(2026, 7, 14), date(2026, 7, 14))

def test_extract_date_range_iso_format():
    result = extract_date_range("Find memories from 2026-08-05")
    assert result == (date(2026, 8, 5), date(2026, 8, 5))

def test_extract_date_range_two_dates_returns_span():
    result = extract_date_range("What happened between July 25 and July 30, 2026?")
    assert result == (date(2026, 7, 25), date(2026, 7, 30))

def test_extract_date_range_month_year_expands_to_full_month():
    start, end = extract_date_range("What was going on in August 2026?")
    assert start == date(2026, 8, 1)
    assert end == date(2026, 8, 31)

def test_extract_date_range_first_week_of_month():
    start, end = extract_date_range("first week of August 2026")
    assert start == date(2026, 8, 1)
    assert end == date(2026, 8, 7)

def test_extract_date_range_second_week_of_month():
    start, end = extract_date_range("second week of August 2026")
    assert start == date(2026, 8, 8)
    assert end == date(2026, 8, 14)

def test_extract_date_range_no_date_returns_none():
    assert extract_date_range("What do I know about bakeries?") is None

def test_extract_date_range_month_year_not_consumed_as_full_date():
    # "August 2026" should NOT parse "20" as the day (regression for the \b fix)
    result = extract_date_range("first week of August 2026")
    assert result is not None
    start, _ = result
    assert start.day == 1


# ---------------------------------------------------------------------------
# rerank_by_date
# ---------------------------------------------------------------------------

def _make_memory(date_str, distance=1.0):
    return {
        "distance": distance,
        "metadata": {"date": date_str},
    }

def test_rerank_by_date_boosts_matching_memory():
    memories = [_make_memory("2026-07-14", distance=1.0)]
    date_range = (date(2026, 7, 14), date(2026, 7, 14))
    result = rerank_by_date(memories, date_range)
    assert result[0]["distance"] == pytest.approx(1.0 * DATE_BOOST_FACTOR)

def test_rerank_by_date_does_not_boost_outside_range():
    memories = [_make_memory("2026-07-01", distance=1.0)]
    date_range = (date(2026, 7, 14), date(2026, 7, 14))
    result = rerank_by_date(memories, date_range)
    assert result[0]["distance"] == pytest.approx(1.0)

def test_rerank_by_date_boosts_within_range():
    memories = [
        _make_memory("2026-07-25", distance=1.0),
        _make_memory("2026-07-28", distance=1.0),
        _make_memory("2026-07-31", distance=1.0),  # outside
    ]
    date_range = (date(2026, 7, 25), date(2026, 7, 30))
    result = rerank_by_date(memories, date_range)
    assert result[0]["distance"] == pytest.approx(DATE_BOOST_FACTOR)
    assert result[1]["distance"] == pytest.approx(DATE_BOOST_FACTOR)
    assert result[2]["distance"] == pytest.approx(1.0)

def test_rerank_by_date_falls_back_to_title():
    memory = {"distance": 1.0, "metadata": {"title": "2026-07-14"}}
    result = rerank_by_date([memory], (date(2026, 7, 14), date(2026, 7, 14)))
    assert result[0]["distance"] == pytest.approx(DATE_BOOST_FACTOR)

def test_rerank_by_date_none_range_is_noop():
    memories = [_make_memory("2026-07-14", distance=1.0)]
    result = rerank_by_date(memories, None)
    assert result[0]["distance"] == pytest.approx(1.0)

def test_rerank_by_date_missing_date_field_skipped():
    memory = {"distance": 1.0, "metadata": {}}
    result = rerank_by_date([memory], (date(2026, 7, 14), date(2026, 7, 14)))
    assert result[0]["distance"] == pytest.approx(1.0)
