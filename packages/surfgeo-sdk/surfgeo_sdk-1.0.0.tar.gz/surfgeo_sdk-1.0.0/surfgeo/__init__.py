"""
SurfGEO Python SDK

Track AI bot traffic on your Python servers
"""

__version__ = "1.0.0"

# Core client
from surfgeo.client import surfgeoClient, surfgeoConfig

# Middleware (lazy imports to avoid framework dependencies)
def get_django_middleware():
    from surfgeo.middleware.django import surfgeoMiddleware
    return surfgeoMiddleware


def get_flask_extension():
    from surfgeo.middleware.flask import surfgeo
    return surfgeo


def get_fastapi_middleware():
    from surfgeo.middleware.fastapi import surfgeoMiddleware
    return surfgeoMiddleware


def get_wsgi_middleware():
    from surfgeo.middleware.wsgi import surfgeoWSGIMiddleware
    return surfgeoWSGIMiddleware


def get_asgi_middleware():
    from surfgeo.middleware.asgi import surfgeoASGIMiddleware
    return surfgeoASGIMiddleware


# Types
from surfgeo.types import TrackingPayload, RequestMetadata


__all__ = [
    'surfgeoClient',
    'surfgeoConfig',
    'TrackingPayload',
    'RequestMetadata',
    'get_django_middleware',
    'get_flask_extension',
    'get_fastapi_middleware',
    'get_wsgi_middleware',
    'get_asgi_middleware',
    '__version__',
]

