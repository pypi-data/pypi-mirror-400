# proliferate-ai

Python SDK for Proliferate Error Monitoring.

## Installation

```bash
pip install proliferate-ai
```

## Quick Start

```python
import proliferate

# Initialize the SDK
proliferate.init(
    api_key="pk_your_api_key",
    environment="production",
    release="1.0.0",
)

# Set user context (optional)
proliferate.set_user(id="user_123", email="user@example.com")
```

## Automatic Error Capture

After initialization, the SDK automatically captures:

- Uncaught exceptions (`sys.excepthook`)
- Unhandled exceptions in threads (`threading.excepthook`)

## Manual Error Capture

```python
try:
    risky_operation()
except Exception as e:
    proliferate.capture_exception(e)
```

## FastAPI Integration

```bash
pip install proliferate-ai[fastapi]
```

```python
from fastapi import FastAPI
import proliferate
from proliferate.integrations.fastapi import ProliferateMiddleware

proliferate.init(
    api_key="pk_your_api_key",
    environment="production",
    release="1.0.0",
)

app = FastAPI()
app.add_middleware(ProliferateMiddleware)
```

## Documentation

See [docs.proliferate.dev/sdk/python](https://docs.proliferate.dev/sdk/python) for full documentation.
