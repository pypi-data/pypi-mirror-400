# Fourbyfour Python SDK

Official Python SDK for the Fourbyfour platform.

## Installation

```bash
pip install fourbyfour
```

## Usage

```python
from fourbyfour import Fourbyfour

client = Fourbyfour(api_key="your-api-key")

# Stream
topic = client.stream.topics.create(name="events", partitions=3)
client.stream.topics.produce("events", key="user-1", value={"action": "click"})

# Notifications
client.notifications.send(
    channel="email",
    recipient="user@example.com",
    subject="Hello",
    body="Welcome to Fourbyfour!"
)

# Webhooks
endpoint = client.hooks.create_endpoint(
    url="https://example.com/webhook",
    events=["order.created"]
)
```

## Documentation

See [docs.fourbyfour.dev](https://docs.fourbyfour.dev) for full documentation.
