import hashlib
from typing import Dict, List, Optional


def parse_bearer(header_val: Optional[str]) -> Optional[str]:
    if not header_val:
        return None

    parts = header_val.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1].strip()

    # Handle accidentally quoted tokens
    if token.startswith('"') and token.endswith('"'):
        token = token[1:-1]

    return token or None


def attrs_to_dict(items: Optional[List[Dict[str, str]]]) -> Dict[str, str]:
    """
    Converts Cognito attribute list to dict
    """
    out: Dict[str, str] = {}
    for item in items or []:
        name = item.get("Name")
        value = item.get("Value")
        if name:
            out[name] = value
    return out


def cache_key_for_token(token: str) -> str:
    """
    Stable cache key (safe for memcached/redis)
    """
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"cognito:get_user:{digest}"
