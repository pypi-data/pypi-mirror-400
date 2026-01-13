from typing import TypedDict, Optional, Dict, Union
from dataclasses import dataclass


class TrackingPayload(TypedDict, total=False):
    """Contract-compliant tracking payload"""
    timestamp: int
    path: str
    method: str
    status_code: Optional[int]
    user_agent: str
    referrer: Optional[str]
    headers: Optional[Dict[str, str]]
    request_id: Optional[str]
    script_key: Optional[str]
    source: Optional[str]


class RequestMetadata(TypedDict):
    """Request metadata extracted by middleware"""
    path: str
    method: str
    headers: Dict[str, Union[str, list]]
    status_code: Optional[int]


@dataclass
class surfgeoConfig:
    """SDK configuration"""
    script_key: str
    endpoint: Optional[str] = None
    timeout: float = 0.05
    debug: bool = False
    enabled: bool = True

