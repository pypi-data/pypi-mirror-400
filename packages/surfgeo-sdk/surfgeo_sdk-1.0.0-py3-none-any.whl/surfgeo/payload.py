import time
import uuid
from typing import Dict, Optional, Union
from urllib.parse import urlparse
from surfgeo.types import RequestMetadata, TrackingPayload


def build_payload(metadata: RequestMetadata) -> TrackingPayload:
    """
    Build tracking payload from request metadata

    Args:
        metadata: Extracted request information

    Returns:
        Contract-compliant payload
    """
    return {
        'timestamp': int(time.time()),
        'path': normalize_path(metadata['path']),
        'method': metadata['method'].upper(),
        'status_code': metadata.get('status_code', 200),
        'user_agent': extract_user_agent(metadata['headers']),
        'referrer': extract_referrer(metadata['headers']),
        'request_id': str(uuid.uuid4())
    }


def normalize_path(path: str) -> str:
    """
    Normalize URL path

    - Remove query string
    - Remove trailing slash (except root)
    """
    parsed = urlparse(path)
    normalized = parsed.path

    # Remove trailing slash (except root)
    if len(normalized) > 1 and normalized.endswith('/'):
        normalized = normalized[:-1]

    return normalized


def extract_user_agent(headers: Dict) -> str:
    """
    Extract User-Agent from headers

    Handles case-insensitive headers
    """
    # Try different casings
    for key in ['User-Agent', 'user-agent', 'USER-AGENT']:
        if key in headers:
            value = headers[key]
            # Handle list values (some frameworks)
            if isinstance(value, list):
                return value[0] if value else 'Unknown'
            return value
    return 'Unknown'


def extract_referrer(headers: Dict) -> Optional[str]:
    """
    Extract Referer header

    Note: HTTP spec uses 'Referer' (misspelling)
    """
    for key in ['Referer', 'referer', 'REFERER', 'Referrer', 'referrer']:
        if key in headers:
            value = headers[key]
            if isinstance(value, list):
                return value[0] if value else None
            return value
    return None

