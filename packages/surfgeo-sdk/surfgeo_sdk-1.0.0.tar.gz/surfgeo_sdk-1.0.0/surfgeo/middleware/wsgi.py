from surfgeo.client import surfgeoClient, surfgeoConfig
from surfgeo.payload import build_payload
from typing import Callable, Iterable


class surfgeoWSGIMiddleware:
    """
    Generic WSGI middleware

    Usage:
        from wsgiref.simple_server import make_server

        app = your_wsgi_app
        app = surfgeoWSGIMiddleware(app, script_key='sk_your_key')

        server = make_server('', 8000, app)
        server.serve_forever()
    """

    def __init__(self, app: Callable, **config):
        """
        Initialize WSGI middleware

        Args:
            app: WSGI application callable
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

    def __call__(self, environ: dict, start_response: Callable):
        """
        WSGI application interface

        Args:
            environ: WSGI environment dict
            start_response: Start response callable

        Returns:
            Iterable of response body
        """
        # Capture status code via wrapper
        status_code = [200]  # Mutable container

        def custom_start_response(status, response_headers, exc_info=None):
            # Extract status code
            status_code[0] = int(status.split()[0])
            return start_response(status, response_headers, exc_info)

        # Call wrapped app
        response = self.app(environ, custom_start_response)

        # Extract metadata
        metadata = {
            'path': environ.get('PATH_INFO', '/'),
            'method': environ.get('REQUEST_METHOD', 'GET'),
            'headers': self._extract_headers_from_environ(environ),
            'status_code': status_code[0]
        }

        # Build payload
        payload = build_payload(metadata)

        # Track (non-blocking)
        self.client.track(payload)

        # Return response
        return response

    def _extract_headers_from_environ(self, environ: dict) -> dict:
        """
        Extract HTTP headers from WSGI environ

        WSGI stores headers as HTTP_* keys
        """
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_USER_AGENT to User-Agent
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value

        # Special cases
        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in environ:
            headers['Content-Length'] = environ['CONTENT_LENGTH']

        return headers

