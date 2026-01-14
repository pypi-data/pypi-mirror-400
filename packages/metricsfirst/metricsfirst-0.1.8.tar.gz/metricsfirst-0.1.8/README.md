# MetricsFirst Python SDK

Official Python SDK for [MetricsFirst](https://metricsfirst.com) - Analytics for Telegram bots.

> **Note:** Commands and interactions are tracked automatically when you add your bot to MetricsFirst. This SDK is for tracking custom events like services, purchases, and errors.

## Installation

```bash
# Basic installation (sync only)
pip install metricsfirst

# With async support
pip install metricsfirst[async]
```

## Features

- **Fire-and-forget**: All tracking calls are non-blocking and don't add latency
- **Background sending**: Events are sent in a separate thread (sync) or task (async)
- **Auto cleanup**: No need to call shutdown() - events flush automatically on exit
- **Error resilience**: Errors are logged, never thrown to your code
- **Memory safe**: Queue is limited to 1000 events to prevent memory issues
- **Custom Events**: Track any event with dynamic properties (Mixpanel-style)

## Quick Start

### Custom Events (Mixpanel-style)

Track any event with dynamic properties:

```python
from metricsfirst import MetricsFirst

# Initialize once (globally)
mf = MetricsFirst(
    bot_id="your_bot_id",
    api_key="your_api_key",
)

# Track custom events with any properties
mf.track(123456789, 'STORY_RESPONSE', {
    'target': 'username123',
    'url': 'https://example.com/story',
    'response_time_ms': 150,
    'success': True,
})

mf.track(123456789, 'BUTTON_CLICK', {
    'button_name': 'premium_upgrade',
    'screen': 'main_menu',
})

mf.track(123456789, 'VIDEO_DOWNLOADED', {
    'duration_seconds': 45,
    'quality': '1080p',
    'source': 'instagram',
})

# Events are automatically flushed on exit - no shutdown() needed!
```

### Synchronous Client

```python
from metricsfirst import MetricsFirst, ServiceEventData

# Initialize once (globally)
mf = MetricsFirst(
    bot_id="your_bot_id",
    api_key="your_api_key",
)

# Track a service (fire-and-forget, non-blocking)
mf.track_service(ServiceEventData(
    user_id=123456789,
    service_name="image_generation",
    is_free=False,
    price=10,
    currency="USD",
))

# Events are automatically flushed on exit
```

### Asynchronous Client

```python
import asyncio
from metricsfirst import AsyncMetricsFirst, ServiceEventData

# Initialize once (globally)
mf = AsyncMetricsFirst(
    bot_id="your_bot_id",
    api_key="your_api_key",
)

async def main():
    # Just use it - auto-starts on first call
    await mf.track_service(ServiceEventData(
        user_id=123456789,
        service_name="image_generation",
    ))

# Events are automatically flushed on exit
asyncio.run(main())
```

### Context Manager

```python
# Sync
with MetricsFirst(bot_id="...", api_key="...") as mf:
    mf.track_service(...)

# Async
async with AsyncMetricsFirst(bot_id="...", api_key="...") as mf:
    await mf.track_service(...)
```

## Available Methods

| Method                             | Description                                 |
| ---------------------------------- | ------------------------------------------- |
| `track()`                          | **Track custom events with any properties** |
| `track_service()`                  | Track services provided                     |
| `track_error()`                    | Track errors                                |
| `track_error_from_exception()`     | Track error from exception                  |
| `track_purchase_initiated()`       | Track purchase start                        |
| `track_purchase_completed()`       | Track successful purchase                   |
| `track_purchase_error()`           | Track failed purchase                       |
| `track_recurring_charge_success()` | Track subscription charge                   |
| `track_recurring_charge_failed()`  | Track failed charge                         |
| `identify()`                       | Identify user with properties               |

### track() - Custom Events

```python
mf.track(
    user_id: int,                 # Telegram user ID
    event_name: str,              # Event name (e.g., 'STORY_RESPONSE')
    properties: dict = None,      # Any key-value pairs
)
```

## Configuration

```python
mf = MetricsFirst(
    bot_id="your_bot_id",
    api_key="your_api_key",
    api_url="https://api.metricsfirst.com",  # Custom API URL
    batch_events=True,      # Batch events before sending
    batch_size=10,          # Events per batch
    batch_interval=5.0,     # Seconds between flushes
    debug=False,            # Enable debug logging
    timeout=10.0,           # HTTP timeout
)
```

## License

MIT
