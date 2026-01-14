# Statly Observe SDK for Python

[![PyPI version](https://img.shields.io/pypi/v/statly-observe.svg)](https://pypi.org/project/statly-observe/)
[![Python versions](https://img.shields.io/pypi/pyversions/statly-observe.svg)](https://pypi.org/project/statly-observe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Error tracking and monitoring for Python applications. Capture exceptions, track releases, and debug issues faster.

**[📚 Full Documentation](https://docs.statly.live/sdk/python/installation)** | **[🚀 Get Started](https://statly.live)** | **[💬 Support](mailto:support@mail.kodydennon.com)**

> **This SDK requires a [Statly](https://statly.live) account.** Sign up free at [statly.live](https://statly.live) to get your DSN and start tracking errors in minutes.

## Features

- Automatic exception capturing with full stack traces
- **Structured Logging**: Production-grade logging with automatic scrubbing
- **Distributed Tracing**: Track function execution and latency across your app
- **Performance Monitoring**: Measure execution time and success rates
- Breadcrumbs for debugging context
- User context tracking
- Release tracking
- Framework integrations (Flask, Django, FastAPI)
- Async support
- Minimal overhead

## Installation

```bash
pip install statly-observe
```

With framework integrations:

```bash
pip install statly-observe[flask]     # Flask support
pip install statly-observe[django]    # Django support
pip install statly-observe[fastapi]   # FastAPI/Starlette support
pip install statly-observe[all]       # All integrations
```

## Getting Your DSN

1. Go to [statly.live/dashboard/observe/setup](https://statly.live/dashboard/observe/setup)
2. Create an API key for Observe
3. Copy your DSN (format: `https://<api-key-prefix>@statly.live/<org-slug>`)
   - Notice: The DSN uses a public 16-character prefix (e.g., `sk_live_a1b2c3d4`) and is safe for client-side use.
4. Add to your `.env` file: `STATLY_DSN=https://...`

## Quick Start

The SDK automatically loads DSN from environment variables, so you can simply:

```python
from statly_observe import Statly

# Auto-loads STATLY_DSN from environment
Statly.init()
```

Or pass it explicitly:

```python
from statly_observe import Statly

# Initialize the SDK
Statly.init(
    dsn="https://sk_live_a1b2c3d4@statly.live/your-org",
    environment="production",
    release="1.0.0",
)

# Errors are captured automatically via sys.excepthook

# Manual capture
try:
    risky_operation()
except Exception as e:
    Statly.capture_exception(e)

# Capture a message
Statly.capture_message("User completed checkout", level="info")

# Set user context
Statly.set_user(
    id="user-123",
    email="user@example.com",
)

# Add breadcrumb for debugging
Statly.add_breadcrumb(
    message="User logged in",
    category="auth",
    level="info",
)

# Always close before exit
Statly.close()
```

## Tracing & Performance

Statly Observe supports distributed tracing to help you visualize function execution and measure performance.

### Automatic Tracing (Decorators)

Use the `@Statly.trace()` decorator to automatically time functions and capture their results:

```python
from statly_observe import Statly

@Statly.trace("process_order", tags={"priority": "high"})
async def handle_order(order_id):
    # This function is now automatically timed
    # Any exceptions will be linked to this span
    result = await database.save(order_id)
    return result
```

### Manual Spans

For more granular control, you can start and finish spans manually:

```python
span = Statly.start_span("heavy_computation")
try:
    # Perform operation
    do_work()
    span.set_tag("items_processed", "100")
finally:
    span.finish() # Sends data to Statly
```

## Structured Logging

The Logger class provides production-grade structured logging with automatic secret scrubbing, session management, and batching.

### Quick Start

```python
from statly_observe import Logger

logger = Logger(
    dsn='https://sk_live_xxx@statly.live/your-org',
    environment='production',
    logger_name='api-server',
)

# Log at different levels
logger.trace('Entering function', args=[1, 2, 3])
logger.debug('Processing request', request_id='req_123')
logger.info('User logged in', user_id='user_123')
logger.warn('Rate limit approaching', current=95, limit=100)
logger.error('Payment failed', order_id='ord_456', error='Card declined')
logger.fatal('Database connection lost', host='db.example.com')
logger.audit('User role changed', user_id='user_123', new_role='admin')

# Always close before exit
logger.close()
```

### Context Manager

Use the logger as a context manager for automatic cleanup:

```python
with Logger(dsn='...') as logger:
    logger.info('Processing...')
# Automatically flushed and closed
```

### Child Loggers

Create child loggers with inherited context:

```python
request_logger = logger.child(
    context={'request_id': 'req_123'},
    logger_name='request-handler',
)

request_logger.info('Processing request')  # Includes request_id automatically
```

### User Context

Associate logs with users:

```python
logger.set_user(
    id='user_123',
    email='jane@example.com',
    name='Jane Doe',
)
```

### Secret Scrubbing

The logger automatically scrubs sensitive data (API keys, passwords, credit cards, etc.). Add custom patterns:

```python
logger = Logger(
    dsn='...',
    scrub_patterns=[
        r'my-custom-secret-[a-z0-9]+',
        r'internal-token-\d+',
    ],
)
```

### Sample Rates

Control log volume with per-level sampling:

```python
logger = Logger(
    dsn='...',
    sample_rates={
        'trace': 0.01,   # 1% of trace logs
        'debug': 0.1,    # 10% of debug logs
        'info': 0.5,     # 50% of info logs
        'warn': 1.0,     # 100% of warnings
        'error': 1.0,    # 100% of errors
        'fatal': 1.0,    # 100% of fatal
    },
)
```

### Logger Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dsn` | `str` | required | Your project's Data Source Name |
| `environment` | `str` | `None` | Environment name |
| `release` | `str` | `None` | Release/version identifier |
| `logger_name` | `str` | `None` | Logger name for filtering |
| `session_id` | `str` | auto-generated | Session ID for grouping logs |
| `user` | `dict` | `None` | User context |
| `default_context` | `dict` | `{}` | Default context for all logs |
| `min_level` | `str` | `'trace'` | Minimum level to log |
| `sample_rates` | `dict` | all 1.0 | Per-level sample rates |
| `scrub_patterns` | `list[str]` | `[]` | Additional regex patterns to scrub |
| `batch_size` | `int` | `50` | Batch size before flush |
| `flush_interval` | `float` | `5.0` | Flush interval in seconds |
| `max_queue_size` | `int` | `1000` | Max queue size |

## Framework Integrations

### Flask

```python
from flask import Flask
from statly_observe import Statly
from statly_observe.integrations.flask import init_flask

app = Flask(__name__)

# Initialize Statly
Statly.init(
    dsn="https://sk_live_a1b2c3d4@statly.live/your-org",
    environment="production",
)

# Attach to Flask app
init_flask(app)

@app.route("/")
def index():
    return "Hello World"

@app.route("/error")
def error():
    raise ValueError("Test error")  # Automatically captured
```

### Django

**settings.py:**

```python
INSTALLED_APPS = [
    # ...
    'statly_observe.integrations.django',
]

MIDDLEWARE = [
    'statly_observe.integrations.django.StatlyMiddleware',
    # ... other middleware (Statly should be first)
]

# Statly configuration
STATLY_DSN = "https://sk_live_xxx@statly.live/your-org"
STATLY_ENVIRONMENT = "production"
STATLY_RELEASE = "1.0.0"
```

**wsgi.py or manage.py:**

```python
from statly_observe import Statly
from django.conf import settings

Statly.init(
    dsn=settings.STATLY_DSN,
    environment=settings.STATLY_ENVIRONMENT,
    release=settings.STATLY_RELEASE,
)
```

### FastAPI

```python
from fastapi import FastAPI
from statly_observe import Statly
from statly_observe.integrations.fastapi import init_fastapi

app = FastAPI()

# Initialize Statly
Statly.init(
    dsn="https://sk_live_a1b2c3d4@statly.live/your-org",
    environment="production",
)

# Attach to FastAPI app
init_fastapi(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/error")
async def error():
    raise ValueError("Test error")  # Automatically captured
```

### Generic WSGI/ASGI

```python
from statly_observe import Statly
from statly_observe.integrations.wsgi import StatlyWSGIMiddleware
from statly_observe.integrations.asgi import StatlyASGIMiddleware

Statly.init(dsn="https://sk_live_xxx@statly.live/your-org")

# WSGI
app = StatlyWSGIMiddleware(your_wsgi_app)

# ASGI
app = StatlyASGIMiddleware(your_asgi_app)
```

## Environment Variables

The SDK automatically loads configuration from environment variables:

| Variable | Description |
|----------|-------------|
| `STATLY_DSN` | Your project's DSN (primary) |
| `STATLY_OBSERVE_DSN` | Alternative DSN variable |
| `STATLY_ENVIRONMENT` | Environment name |
| `PYTHON_ENV` or `ENV` | Fallback for environment |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dsn` | `str` | `os.environ["STATLY_DSN"]` | Your project's Data Source Name |
| `environment` | `str` | `None` | Environment name (production, staging, development) |
| `release` | `str` | `None` | Release/version identifier for tracking |
| `debug` | `bool` | `False` | Enable debug logging to stderr |
| `sample_rate` | `float` | `1.0` | Sample rate for events (0.0 to 1.0) |
| `max_breadcrumbs` | `int` | `100` | Maximum breadcrumbs to store |
| `before_send` | `callable` | `None` | Callback to modify/filter events before sending |

### before_send Example

```python
def before_send(event):
    # Filter out specific errors
    if "KeyboardInterrupt" in event.get("message", ""):
        return None  # Drop the event

    # Scrub sensitive data
    if "extra" in event and "password" in event["extra"]:
        del event["extra"]["password"]

    return event

Statly.init(
    dsn="...",
    before_send=before_send,
)
```

## API Reference

### Statly.capture_exception(exception, **context)

Capture an exception with optional additional context:

```python
try:
    process_payment(order)
except PaymentError as e:
    Statly.capture_exception(
        e,
        extra={
            "order_id": order.id,
            "amount": order.total,
        },
        tags={
            "payment_provider": "stripe",
        },
    )
```

### Statly.capture_message(message, level="info")

Capture a message event:

```python
Statly.capture_message("User signed up", level="info")
Statly.capture_message("Payment failed after 3 retries", level="warning")
Statly.capture_message("Database connection lost", level="error")
```

Levels: `"debug"` | `"info"` | `"warning"` | `"error"` | `"fatal"`

### Statly.set_user(**kwargs)

Set user context for all subsequent events:

```python
Statly.set_user(
    id="user-123",
    email="user@example.com",
    username="johndoe",
    # Custom fields
    subscription="premium",
)

# Clear user on logout
Statly.set_user(None)
```

### Statly.set_tag(key, value) / Statly.set_tags(tags)

Set tags for filtering and searching:

```python
Statly.set_tag("version", "1.0.0")

Statly.set_tags({
    "environment": "production",
    "server": "web-1",
    "region": "us-east-1",
})
```

### Statly.add_breadcrumb(**kwargs)

Add a breadcrumb for debugging context:

```python
Statly.add_breadcrumb(
    message="User clicked checkout button",
    category="ui.click",
    level="info",
    data={
        "button_id": "checkout-btn",
        "cart_items": 3,
    },
)
```

### Statly.flush() / Statly.close()

```python
# Flush pending events (keeps SDK running)
Statly.flush()

# Flush and close (use before process exit)
Statly.close()
```

## Context Manager

Use context manager for automatic cleanup:

```python
from statly_observe import Statly

with Statly.init(dsn="...") as client:
    # Your code here
    pass
# Automatically flushed and closed
```

## Async Support

The SDK automatically detects async contexts:

```python
import asyncio
from statly_observe import Statly

async def main():
    Statly.init(dsn="...")

    try:
        await risky_async_operation()
    except Exception as e:
        Statly.capture_exception(e)

    await Statly.flush_async()

asyncio.run(main())
```

## Logging Integration

Capture Python logging as breadcrumbs or events:

```python
import logging
from statly_observe import Statly
from statly_observe.integrations.logging import StatlyHandler

Statly.init(dsn="...")

# Add handler to capture logs as breadcrumbs
handler = StatlyHandler(level=logging.INFO)
logging.getLogger().addHandler(handler)

# Now logs are captured
logging.info("User logged in")  # Becomes a breadcrumb
logging.error("Database error")  # Captured as error event
```

## Requirements

- Python 3.8+
- Works with sync and async code

## Resources

- **[Statly Platform](https://statly.live)** - Sign up and manage your error tracking
- **[Documentation](https://docs.statly.live/sdk/python/installation)** - Full SDK documentation
- **[API Reference](https://docs.statly.live/sdk/python/api-reference)** - Complete API reference
- **[Flask Guide](https://docs.statly.live/sdk/python/flask)** - Flask integration
- **[Django Guide](https://docs.statly.live/sdk/python/django)** - Django integration
- **[FastAPI Guide](https://docs.statly.live/sdk/python/fastapi)** - FastAPI integration
- **[MCP Server](https://github.com/KodyDennon/DD-StatusPage/tree/master/packages/mcp-docs-server)** - AI/Claude integration for docs

## Why Statly?

Statly is more than error tracking. Get:
- **Status Pages** - Beautiful public status pages for your users
- **Uptime Monitoring** - Multi-region HTTP/DNS checks every minute
- **Error Tracking** - SDKs for JavaScript, Python, and Go
- **Incident Management** - Track and communicate outages

All on Cloudflare's global edge network. [Start free →](https://statly.live)

## License

MIT
