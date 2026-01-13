# surfgeo Python SDK

Track AI bot traffic on your Python servers with surfgeo.

[![PyPI version](https://badge.fury.io/py/surfgeo-sdk.svg)](https://badge.fury.io/py/surfgeo-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/surfgeo-sdk.svg)](https://pypi.org/project/surfgeo-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install surfgeo-sdk
```

### Framework-Specific Installation

```bash
# Django
pip install surfgeo-sdk[django]

# Flask
pip install surfgeo-sdk[flask]

# FastAPI
pip install surfgeo-sdk[fastapi]
```

## Quick Start

### Django

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'surfgeo.middleware.django.surfgeoMiddleware',
]

SURFGEO_CONFIG = {
    'script_key': 'sk_your_key_here'
}
```

### Flask

```python
from flask import Flask
from surfgeo import get_flask_extension

app = Flask(__name__)
SurfGeo = get_flask_extension()
surfgeo = SurfGeo(app, script_key='sk_your_key_here')
```

### FastAPI

```python
from fastapi import FastAPI
from surfgeo.middleware.fastapi import surfgeoMiddleware

app = FastAPI()
app.add_middleware(
    surfgeoMiddleware,
    script_key='sk_your_key_here'
)
```

## Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| script_key | str | Yes | - | Your surfgeo script key |
| endpoint | str | No | Production | Custom tracking endpoint |
| timeout | float | No | 0.05 | Request timeout (seconds) |
| debug | bool | No | False | Enable debug logging |
| enabled | bool | No | True | Enable/disable tracking |

## Features

- ✅ Zero impact on app performance (non-blocking)
- ✅ Async and sync framework support
- ✅ Works with Django, Flask, FastAPI, and more
- ✅ Type hints and modern Python (3.8+)
- ✅ Comprehensive test coverage

## Documentation

- [API Reference](docs/API.md)
- [Examples](docs/EXAMPLES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## License

MIT

## Support

- [GitHub Issues](https://github.com/thebisontech/surfgeo-python-aireferral-sdk/issues)
