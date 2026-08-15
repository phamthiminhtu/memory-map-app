import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from dateutil import parser as dateutil_parser
from backend.utils.constants.text_parsing import (
    DATE_BOOST_FACTOR,
    FULL_DATE_RE,
    MONTH_YEAR_RE,
    WEEK_OF_MONTH_RE,
    YEAR_RE,
)

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def split_into_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately equal size"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_size += len(word) + 1
        if current_size > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def extract_date_range(query: str) -> Optional[Tuple[date, date]]:
    """Return (start, end) date range extracted from the query, or None."""
    year_match = YEAR_RE.search(query)
    default_year = int(year_match.group(1)) if year_match else date.today().year

    month_year_match = MONTH_YEAR_RE.search(query)
    if month_year_match and not FULL_DATE_RE.search(query):
        anchor = dateutil_parser.parse(f"{month_year_match.group(1)} 1 {month_year_match.group(2)}").date()
        week_match = WEEK_OF_MONTH_RE.search(query)
        if week_match:
            week_num = {"first": 0, "second": 1, "third": 2, "fourth": 3}[week_match.group(1).lower()]
            start = anchor + timedelta(weeks=week_num)
            return start, start + timedelta(days=6)
        next_month = (anchor.replace(day=28) + timedelta(days=4)).replace(day=1)
        return anchor, next_month - timedelta(days=1)

    raw_dates = FULL_DATE_RE.findall(query)
    if not raw_dates:
        return None

    parsed = []
    for raw in raw_dates:
        try:
            parsed.append(dateutil_parser.parse(raw, default=datetime(default_year, 1, 1)).date())
        except Exception:
            pass

    if not parsed:
        return None

    parsed.sort()
    return parsed[0], parsed[-1]


def rerank_by_date(memories: List[Dict[str, Any]], date_range: Optional[Tuple[date, date]]) -> List[Dict[str, Any]]:
    """Boost distance score for memories whose date falls within date_range."""
    if date_range is None:
        return memories
    start, end = date_range
    for memory in memories:
        meta = memory.get("metadata", {})
        raw_date = meta.get("date") or meta.get("title") or meta.get("timestamp", "")
        if not raw_date:
            continue
        try:
            mem_date = dateutil_parser.parse(str(raw_date)[:10]).date()
            if start <= mem_date <= end:
                memory["distance"] = memory.get("distance", 1.0) * DATE_BOOST_FACTOR
        except Exception:
            pass
    return memories