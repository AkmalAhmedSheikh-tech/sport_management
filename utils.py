from werkzeug.security import generate_password_hash, check_password_hash
def hash_password(password: str) -> str:
    """
    Takes a plaintext password and returns a salted hash.
    """
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Compares a stored hash with a plaintext password.
    Returns True if password is correct.
    """
    return check_password_hash(stored_hash, password)

import re
from datetime import datetime, date, timezone

def slugify(text: str) -> str:
    """
    Very small slugifier: lowercases, removes non-alnum, replaces spaces with '-'.
    Example: "Intercity Cup 2025" -> "intercity-cup-2025"
    """
    if not text:
        return ''
    s = text.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

def utcnow() -> datetime:
    """Naive UTC 'now' (replacement for the deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def now_iso():
    return utcnow().isoformat() + 'Z'

def parse_date(value):
    """
    Parse a 'YYYY-MM-DD' string (as sent by <input type="date">) into a date.
    Returns None for empty input; raises ValueError for an invalid date.
    """
    value = (value or '').strip()
    if not value:
        return None
    return date.fromisoformat(value)
