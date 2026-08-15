import re

DATE_BOOST_FACTOR = 0.5

FULL_DATE_RE = re.compile(
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2}\b(?:,\s*\d{4})?'
    r'|\d{4}-\d{2}-\d{2}\b',
    re.IGNORECASE,
)
MONTH_YEAR_RE = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+(20\d{2})\b',
    re.IGNORECASE,
)
WEEK_OF_MONTH_RE = re.compile(r'\b(first|second|third|fourth)\s+week\b', re.IGNORECASE)
YEAR_RE = re.compile(r'\b(20\d{2})\b')
