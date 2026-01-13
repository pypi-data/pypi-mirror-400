from typing import Callable
from django.http import HttpRequest, HttpResponse
from surfgeo.client import surfgeoClient, surfgeoConfig
from surfgeo.payload import build_payload


class surfgeoMiddleware:
    """
    Django middleware for tracking AI bot traffic

    Usage:
        MIDDLEWARE = [
            # ... other middleware
            'surfgeo.middleware.django.surfgeoMiddleware',
        ]

        SURFGEO_CONFIG = {
            'script_key': 'sk_your_key_here',
            'debug': DEBUG
        }
    """

    def __init__(self, get_response: Callable):
        """
        Initialize middleware once when Django starts

        Steps:
        1. Store get_response callable
        2. Load config from Django settings
        3. Initialize surfgeoClient
        4. Validate config
        """
        self.get_response = get_response

        # Load config from settings
        from django.conf import settings
        config_dict = getattr(settings, 'SURFGEO_CONFIG', {})

        # Create config object
        self.config = surfgeoConfig(
            script_key=config_dict.get('script_key', ''),
            endpoint=config_dict.get('endpoint'),
            timeout=config_dict.get('timeout', 0.05),
            debug=config_dict.get('debug', False),
            enabled=config_dict.get('enabled', True)
        )

        # Initialize client
        self.client = surfgeoClient(self.config)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request

        Flow:
        1. Call next middleware/view (get response)
        2. Extract metadata after response is ready
        3. Track in background (non-blocking)
        4. Return response immediately
        """
        # Get response first (middleware chain)
        response = self.get_response(request)

        # Extract metadata after response is ready
        # Handle both Django 2.2+ (headers) and older (META)
        headers = {}
        if hasattr(request, 'headers'):
            headers = dict(request.headers)
        else:
            # Fallback for older Django versions
            for key, value in request.META.items():
                if key.startswith('HTTP_'):
                    header_name = key[5:].replace('_', '-').title()
                    headers[header_name] = value

        metadata = {
            'path': request.path,
            'method': request.method,
            'headers': headers,
            'status_code': response.status_code
        }

        # Build payload
        payload = build_payload(metadata)

        # Track (fire-and-forget, doesn't block)
        self.client.track(payload)

        # Return response immediately
        return response

