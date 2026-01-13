from surfgeo.client import surfgeoClient, surfgeoConfig
from surfgeo.payload import build_payload
from typing import Callable


class surfgeoASGIMiddleware:
    """
    Generic ASGI middleware

    Usage:
        from starlette.applications import Starlette

        app = Starlette()
        app = surfgeoASGIMiddleware(app, script_key='sk_your_key')
    """

    def __init__(self, app: Callable, **config):
        """
        Initialize ASGI middleware

        Args:
            app: ASGI application callable
            **config: Configuration options
        """
        self.app = app

        # Create config
        surf_config = surfgeoConfig(
            script_key=config.get('script_key', ''),
            endpoint=config.get('endpoint'),
            timeout=config.get('timeout', 0.05),
            debug=config.get('debug', False),
            enabled=config.get('enabled', True)
        )

        # Initialize client
        self.client = surfgeoClient(surf_config)

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        """
        ASGI application interface

        Args:
            scope: ASGI scope dict
            receive: Receive callable
            send: Send callable
        """
        # Only process HTTP requests
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        # Capture status code
        status_code = [200]

        async def custom_send(message):
            # Capture status from response.start message
            if message['type'] == 'http.response.start':
                status_code[0] = message['status']
            await send(message)

        # Call wrapped app
        await self.app(scope, receive, custom_send)

        # Extract metadata
        metadata = {
            'path': scope.get('path', '/'),
            'method': scope.get('method', 'GET'),
            'headers': self._extract_headers_from_scope(scope),
            'status_code': status_code[0]
        }

        # Build payload
        payload = build_payload(metadata)

        # Track async
        await self.client.track_async(payload)

    def _extract_headers_from_scope(self, scope: dict) -> dict:
        """
        Extract headers from ASGI scope

        ASGI stores headers as list of tuples (bytes)
        """
        headers = {}
        for header_name, header_value in scope.get('headers', []):
            name = header_name.decode('latin1')
            value = header_value.decode('latin1')
            headers[name] = value
        return headers

