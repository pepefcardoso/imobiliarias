import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def parse_price(raw: Optional[str]) -> Optional[float]:
    """
    Extracts a float price from a raw string.

    Handles formats like:
        "R$ 450.000,00"  → 450000.0
        "450,000.00"     → 450000.0
        "1.200.000"      → 1200000.0
        "350000"         → 350000.0

    Returns None if the value cannot be parsed.
    """
    if not raw:
        return None

    cleaned = normalize_whitespace(raw)

    # Remove currency symbols and non-numeric chars except digits, dots and commas
    cleaned = re.sub(r"[^\d.,]", "", cleaned)

    if not cleaned:
        return None

    # Determine format: if both separators exist, identify which is decimal
    has_dot = "." in cleaned
    has_comma = "," in cleaned

    if has_dot and has_comma:
        # Last separator is the decimal one
        last_dot = cleaned.rfind(".")
        last_comma = cleaned.rfind(",")

        if last_comma > last_dot:
            # Format: 1.200.000,00 → remove dots, replace comma with dot
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # Format: 1,200,000.00 → remove commas
            cleaned = cleaned.replace(",", "")
    elif has_comma:
        # Could be thousands (1,200,000) or decimal (450,50)
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal: "450,50" → "450.50"
            cleaned = cleaned.replace(",", ".")
        else:
            # Likely thousands separator: "1,200,000" → "1200000"
            cleaned = cleaned.replace(",", "")
    elif has_dot:
        parts = cleaned.split(".")
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal: "450.50" → keep as is
            pass
        else:
            # Likely thousands separator: "1.200.000" → "1200000"
            cleaned = cleaned.replace(".", "")

    return safe_float(cleaned)


def parse_area(raw: Optional[str]) -> Optional[float]:
    """
    Extracts a float area value (m²) from a raw string.

    Handles formats like:
        "95 m²"     → 95.0
        "95,5m2"    → 95.5
        "1.200 m²"  → 1200.0
        "95.50"     → 95.5

    Returns None if the value cannot be parsed.
    """
    if not raw:
        return None

    cleaned = normalize_whitespace(raw)

    # Extract numeric part (digits, dot, comma) before any unit
    match = re.search(r"[\d.,]+", cleaned)
    if not match:
        return None

    numeric = match.group()

    has_dot = "." in numeric
    has_comma = "," in numeric

    if has_dot and has_comma:
        last_dot = numeric.rfind(".")
        last_comma = numeric.rfind(",")

        if last_comma > last_dot:
            numeric = numeric.replace(".", "").replace(",", ".")
        else:
            numeric = numeric.replace(",", "")
    elif has_comma:
        parts = numeric.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            numeric = numeric.replace(",", ".")
        else:
            numeric = numeric.replace(",", "")
    elif has_dot:
        parts = numeric.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) > 2):
            numeric = numeric.replace(".", "")

    return safe_float(numeric)


def safe_int(raw: Optional[str | int | float]) -> Optional[int]:
    """
    Safely converts a value to int.

    Returns None if conversion fails.
    """
    if raw is None:
        return None

    if isinstance(raw, int):
        return raw

    if isinstance(raw, float):
        return int(raw)

    cleaned = normalize_whitespace(str(raw))
    match = re.search(r"\d+", cleaned)
    if not match:
        return None

    try:
        return int(match.group())
    except (ValueError, TypeError):
        return None


def safe_float(raw: Optional[str | int | float]) -> Optional[float]:
    """
    Safely converts a value to float.

    Returns None if conversion fails.
    """
    if raw is None:
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    try:
        return float(str(raw).strip())
    except (ValueError, TypeError):
        return None


def normalize_whitespace(raw: Optional[str]) -> str:
    """
    Strips leading/trailing whitespace and collapses internal whitespace.

    Returns empty string if input is None.
    """
    if not raw:
        return ""

    return re.sub(r"\s+", " ", raw).strip()


def build_absolute_url(base_url: str, path: str) -> str:
    """
    Converts a relative path into an absolute URL given a base URL.

    Examples:
        base="https://agency.com/listings", path="/property/123"
        → "https://agency.com/property/123"

        base="https://agency.com", path="https://agency.com/property/123"
        → "https://agency.com/property/123"  (already absolute, returned as-is)

    Raises ValueError if the result is not a valid absolute URL.
    """
    if not path:
        raise ValueError("path must not be empty")

    result = urljoin(base_url, path)

    parsed = urlparse(result)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Could not build a valid absolute URL from base='{base_url}' and path='{path}'")

    return result