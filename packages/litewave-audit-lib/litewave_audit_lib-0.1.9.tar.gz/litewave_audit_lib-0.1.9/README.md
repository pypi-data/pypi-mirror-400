# Litewave Audit Library

Internal audit logging library for Litewave services.

## Usage

```python
from litewave_audit_lib.log_factory import get_logger

# Get a logger with NATS backend
logger = get_logger(
    nats_connection_url="nats://username:password@your-nats-server:4222"
)

# Log an audit event
logger.log(
    who="user@email.com",
    resource="document",
    action="view",
    location="cloud",
    request_context={"ip": "127.0.0.1"},
    context={"document_id": "doc123"},
    client={}
)

## Features

- Automatic reconnection handling
- Connection retry logic
- Proper error handling and logging
- Type hints for better IDE support
- Automatic cleanup of NATS connections

## Dependencies

- nats-py (for NATS backend)
