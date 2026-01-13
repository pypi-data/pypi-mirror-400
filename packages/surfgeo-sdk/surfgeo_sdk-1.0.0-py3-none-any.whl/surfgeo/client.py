import threading
import asyncio
from typing import Dict, Optional
import requests
import httpx
from surfgeo.types import surfgeoConfig, TrackingPayload

# Default production endpoint
DEFAULT_ENDPOINT = 'https://api.surfgeo.com/api/track'
DEFAULT_TIMEOUT = 0.05  # 50ms
MAX_TIMEOUT = 0.1  # 100ms
MIN_TIMEOUT = 0.01  # 10ms


class surfgeoClient:
    """Core tracking client for SurfGEO SDK"""

    def __init__(self, config: surfgeoConfig):
        """
        Initialize client with config

        Args:
            config: Configuration object

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate config
        self._validate_config(config)

        # Set defaults
        self.config = surfgeoConfig(
            script_key=config.script_key,
            endpoint=config.endpoint or DEFAULT_ENDPOINT,
            timeout=max(MIN_TIMEOUT, min(config.timeout, MAX_TIMEOUT)),
            debug=config.debug,
            enabled=config.enabled
        )

        self.endpoint = self.config.endpoint

    def validate(self) -> bool:
        """Validate configuration"""
        return self._validate_config(self.config)

    def track(self, payload: Dict) -> None:
        """
        Fire-and-forget tracking (non-blocking)

        Steps:
        1. Check if enabled
        2. Add script_key and source to payload
        3. Start background thread for POST
        4. Return immediately (never blocks)
        """
        if not self.config.enabled:
            return

        full_payload: TrackingPayload = {
            **payload,
            'script_key': self.config.script_key,
            'source': 'server'
        }

        # Start daemon thread (dies with main thread)
        thread = threading.Thread(
            target=self._post,
            args=(full_payload,),
            daemon=True
        )
        thread.start()
        # Return immediately - never wait for thread

    async def track_async(self, payload: Dict) -> None:
        """
        Async fire-and-forget tracking

        Steps:
        1. Check if enabled
        2. Add script_key and source
        3. Create task for POST
        4. Return immediately (don't await)
        """
        if not self.config.enabled:
            return

        full_payload: TrackingPayload = {
            **payload,
            'script_key': self.config.script_key,
            'source': 'server'
        }

        # Create task but don't await
        asyncio.create_task(self._post_async(full_payload))

    def _post(self, payload: Dict) -> None:
        """
        Synchronous HTTP POST with timeout

        Uses:
        - requests library
        - Timeout enforcement
        - Silent failure on error
        """
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.config.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'surfgeo-Python-SDK/1.0.0'
                }
            )
            # Don't check status - backend always returns 200

        except requests.Timeout:
            if self.config.debug:
                print(f"[surfgeo] Request timeout")
        except Exception as e:
            if self.config.debug:
                print(f"[surfgeo] Tracking failed: {e}")
        # Never raise - silent failure

    async def _post_async(self, payload: Dict) -> None:
        """
        Asynchronous HTTP POST with timeout

        Uses:
        - httpx library (async HTTP client)
        - Asyncio timeout
        - Silent failure
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.config.timeout,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'surfgeo-Python-SDK/1.0.0'
                    }
                )
        except httpx.TimeoutException:
            if self.config.debug:
                print(f"[surfgeo] Async request timeout")
        except Exception as e:
            if self.config.debug:
                print(f"[surfgeo] Async tracking failed: {e}")

    def _validate_config(self, config: surfgeoConfig) -> bool:
        """Validate configuration"""
        # Validate script_key
        if not config.script_key:
            raise ValueError('surfgeo: script_key is required')

        if not isinstance(config.script_key, str):
            raise ValueError('surfgeo: script_key must be a string')

        if not config.script_key.startswith('sk_'):
            raise ValueError('surfgeo: script_key must start with "sk_"')

        if len(config.script_key) < 20 or len(config.script_key) > 50:
            raise ValueError('surfgeo: script_key must be between 20 and 50 characters')

        if not config.script_key[3:].replace('_', '').isalnum():
            raise ValueError('surfgeo: script_key must be alphanumeric (underscores allowed) after "sk_" prefix')

        # Validate endpoint if provided
        if config.endpoint is not None:
            try:
                from urllib.parse import urlparse
                urlparse(config.endpoint)
            except Exception:
                raise ValueError('surfgeo: endpoint must be a valid URL')

        # Validate timeout if provided
        if config.timeout is not None:
            if not isinstance(config.timeout, (int, float)) or config.timeout < MIN_TIMEOUT or config.timeout > MAX_TIMEOUT:
                raise ValueError(f'surfgeo: timeout must be between {MIN_TIMEOUT} and {MAX_TIMEOUT} seconds')

        return True

