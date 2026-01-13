from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from surfgeo.client import surfgeoClient, surfgeoConfig
from surfgeo.payload import build_payload


class surfgeoMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware for tracking

    Usage:
        app = FastAPI()
        app.add_middleware(
            surfgeoMiddleware,
            script_key='sk_your_key_here'
        )
    """

    def __init__(self, app, **config):
        """
        Initialize ASGI middleware

        Args:
            app: ASGI application
            **config: Configuration options
        """
        super().__init__(app)

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

    async def dispatch(self, request: Request, call_next):
        """
        Process request (async)

        Flow:
        1. Call next middleware/route handler
        2. Get response
        3. Extract metadata
        4. Track asynchronously (non-blocking)
        5. Return response
        """
        # Call next middleware/handler
        response = await call_next(request)

        # Extract metadata
        metadata = {
            'path': request.url.path,
            'method': request.method,
            'headers': dict(request.headers),
            'status_code': response.status_code
        }

        # Build payload
        payload = build_payload(metadata)

        # Track async (fire-and-forget)
        await self.client.track_async(payload)

        # Return response
        return response

