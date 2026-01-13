from flask import Flask, request
from surfgeo.client import surfgeoClient, surfgeoConfig
from surfgeo.payload import build_payload


class surfgeo:
    """
    Flask extension for SurfGEO tracking

    Usage:
        app = Flask(__name__)
        surfgeo = surfgeo(app, script_key='sk_your_key')

    Or with factory pattern:
        surfgeo = surfgeo()
        surfgeo.init_app(app, script_key='sk_your_key')
    """

    def __init__(self, app: Flask = None, **config):
        """
        Initialize extension

        Args:
            app: Flask application (optional)
            **config: Configuration options
        """
        self.client = None

        if app is not None:
            self.init_app(app, **config)

    def init_app(self, app: Flask, **config):
        """
        Initialize extension with app

        Steps:
        1. Load config from app.config or kwargs
        2. Create surfgeoConfig
        3. Initialize client
        4. Register after_request handler
        """
        # Load config (priority: kwargs > app.config > defaults)
        script_key = config.get('script_key') or \
                     app.config.get('SURFGEO_SCRIPT_KEY')

        endpoint = config.get('endpoint') or \
                   app.config.get('SURFGEO_ENDPOINT')

        timeout = config.get('timeout') or \
                  app.config.get('SURFGEO_TIMEOUT', 0.05)

        debug = config.get('debug') or \
                app.config.get('SURFGEO_DEBUG', False)

        enabled = config.get('enabled', True) and \
                  app.config.get('SURFGEO_ENABLED', True)

        # Create config
        surf_config = surfgeoConfig(
            script_key=script_key or '',
            endpoint=endpoint,
            timeout=timeout,
            debug=debug,
            enabled=enabled
        )

        # Initialize client
        self.client = surfgeoClient(surf_config)

        # Register after_request handler
        app.after_request(self._track_request)

        # Store in app extensions
        app.extensions['surfgeo'] = self

    def _track_request(self, response):
        """
        Track request after response is ready

        Called by Flask after each request

        Args:
            response: Flask Response object

        Returns:
            response (unmodified)
        """
        # Extract metadata
        metadata = {
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'status_code': response.status_code
        }

        # Build payload
        payload = build_payload(metadata)

        # Track (non-blocking)
        self.client.track(payload)

        # Return response unchanged
        return response

