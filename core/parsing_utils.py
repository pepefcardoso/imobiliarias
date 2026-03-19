import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def parse_price(raw: Optional[str | int | float]) -> Optional[float]:
    """
    Extrai um valor de preço (float) a partir de uma string ou número bruto.

    Lida com formatos como:
        "R$ 450.000,00"  → 450000.0
        "450,000.00"     → 450000.0
        "1.200.000"      → 1200000.0
        "350000"         → 350000.0
        450000           → 450000.0 (Novo: Suporte direto a números)

    Retorna None se o valor não puder ser processado.
    """
    if raw is None or raw == "":
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    cleaned = normalize_whitespace(str(raw))

    cleaned = re.sub(r"[^\d.,]", "", cleaned)

    if not cleaned:
        return None

    has_dot = "." in cleaned
    has_comma = "," in cleaned

    if has_dot and has_comma:
        last_dot = cleaned.rfind(".")
        last_comma = cleaned.rfind(",")

        if last_comma > last_dot:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif has_comma:
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif has_dot:
        parts = cleaned.split(".")
        if len(parts) == 2 and len(parts[1]) <= 2:
            pass
        else:
            cleaned = cleaned.replace(".", "")

    return safe_float(cleaned)


def parse_area(raw: Optional[str | int | float]) -> Optional[float]:
    """
    Extrai um valor de área (float, m²) a partir de uma string ou número bruto.

    Lida com formatos como:
        "95 m²"     → 95.0
        "95,5m2"    → 95.5
        "1.200 m²"  → 1200.0
        "95.50"     → 95.5
        95          → 95.0 (Novo: Suporte direto a números)

    Retorna None se o valor não puder ser processado.
    """
    if raw is None or raw == "":
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    cleaned = normalize_whitespace(str(raw))

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
    Converte com segurança um valor para int.

    Retorna None se a conversão falhar.
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
    Converte com segurança um valor para float.

    Retorna None se a conversão falhar.
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
    Remove espaços em branco no início/fim e colapsa espaços internos.

    Retorna uma string vazia se o input for None.
    """
    if not raw:
        return ""

    return re.sub(r"\s+", " ", raw).strip()


def build_absolute_url(base_url: str, path: str) -> str:
    """
    Converte um caminho relativo num URL absoluto dado um URL base.

    Exemplos:
        base="https://agency.com/listings", path="/property/123"
        → "https://agency.com/property/123"

        base="https://agency.com", path="https://agency.com/property/123"
        → "https://agency.com/property/123"  (já é absoluto, retornado como está)

    Levanta ValueError se o resultado não for um URL absoluto válido.
    """
    if not path:
        raise ValueError("path must not be empty")

    result = urljoin(base_url, path)

    parsed = urlparse(result)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Could not build a valid absolute URL from base='{base_url}' and path='{path}'")

    return result