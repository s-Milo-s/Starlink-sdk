# Starlink Enterprise Dashboard SDK

A Python SDK for the Starlink Enterprise Dashboard API, providing type-safe, async-first access to Starlink terminal management, fleet health monitoring, and telemetry data.

# Starlink Enterprise Dashboard SDK

A Python SDK for the Starlink Enterprise Dashboard API, providing type-safe, synchronous access to Starlink terminal management, fleet health monitoring, and telemetry data. 

**Simple and clean - just like the OpenAI SDK!**

## Features

- 🔐 **Automatic Authentication**: Handles token acquisition and automatic rotation
- 🎯 **Simple Synchronous API**: No async/await needed - works like the OpenAI SDK
- 📊 **Type Safety**: Full type hints and Pydantic models for all API responses
- 🔄 **Retry Logic**: Built-in retry handling for robust operation
- 📖 **Pagination Support**: Easy handling of paginated API responses
- 🛡️ **Error Handling**: Comprehensive exception hierarchy for different error types
- ⚙️ **Configurable**: Environment-based configuration for different deployments

## Installation

```bash
pip install starlink-sdk
```

For development:

```bash
pip install starlink-sdk[dev]
```

## Quick Start

### Basic Setup

```python
from datetime import datetime, timedelta
from starlink_sdk import StarlinkClient

# Initialize client - just like OpenAI!
client = StarlinkClient()

# Get fleet health overview
health = client.fleet.get_health(
    from_time=datetime.now() - timedelta(hours=24),
    to_time=datetime.now()
)

print(f"Fleet Status:")
print(f"  Healthy: {health.counts.healthy}")
print(f"  Degraded: {health.counts.degraded}")
print(f"  Offline: {health.counts.offline}")

# List terminals
terminals = client.terminals.list(limit=50)
for terminal in terminals.items:
    print(f"{terminal.terminal_id}: {terminal.status}")

# Get terminal details
terminal = client.terminals.get("TERMINAL_ID_123")
print(f"Health: {terminal.health_status}")
```

### Environment Configuration

Set these environment variables:

```bash
export STARLINK_API_SECRET="your-api-secret-here"
export STARLINK_BASE_URL="https://starlink-enterprise-api.spacex.com"  # optional
```

Or pass them directly:

```python
client = StarlinkClient(
    base_url="https://custom-api.example.com",
    api_secret="your-secret"
)
```

## API Reference

### Fleet Management

#### Get Fleet Health

```python
from datetime import datetime, timedelta

health = client.fleet.get_health(
    from_time=datetime.now() - timedelta(hours=1),
    to_time=datetime.now()
)

print(f"Healthy terminals: {health.counts.healthy}")
if health.top_issues:
    for issue in health.top_issues:
        print(f"Issue: {issue.type} - {issue.count} affected")
```

### Terminal Management

#### List Terminals

```python
from starlink_sdk import TerminalStatus

# List all terminals
terminals = client.terminals.list()

# Filter by status
online_terminals = client.terminals.list(
    status=TerminalStatus.ONLINE,
    limit=100
)

for terminal in online_terminals.items:
    print(f"{terminal.terminal_id}: {terminal.status}")
```

#### Get Terminal Details

```python
terminal = client.terminals.get("TERMINAL_ID_123")

print(f"Terminal: {terminal.name or terminal.terminal_id}")
print(f"Status: {terminal.status}")
print(f"Health: {terminal.health_status}")
print(f"Last seen: {terminal.last_seen}")

if terminal.location:
    print(f"Location: {terminal.location.lat}, {terminal.location.lon}")

if terminal.health_factors:
    print("Health factors:")
    for factor in terminal.health_factors:
        print(f"  {factor.factor}: {factor.value} (threshold: {factor.threshold})")
```

#### Get Terminal Metrics

```python
from starlink_sdk import Interval

metrics = client.terminals.get_metrics(
    terminal_id="TERMINAL_ID_123",
    from_time=datetime.now() - timedelta(hours=6),
    to_time=datetime.now(),
    interval=Interval.FIVE_MINUTES,
    metrics=["latency_ms", "packet_loss_pct", "downlink_mbps"]
)

print(f"Retrieved metrics for {metrics.terminal_id}")
for metric_name, data_points in metrics.series.items():
    print(f"\n{metric_name}:")
    for point in data_points[-5:]:  # Last 5 points
        print(f"  {point.t}: {point.v}")
```

### Alert Management

#### List Alerts

```python
from starlink_sdk import AlertStatus, AlertSeverity

# Get open critical alerts
critical_alerts = client.alerts.list(
    status=AlertStatus.OPEN,
    severity=AlertSeverity.CRITICAL
)

for alert in critical_alerts.items:
    print(f"🚨 {alert.type}: {alert.message}")
    print(f"   Terminal: {alert.terminal_id}")
    print(f"   Created: {alert.created_at}")

# Get alerts for specific terminal
terminal_alerts = client.alerts.list(
    terminal_id="TERMINAL_ID_123",
    from_time=datetime.now() - timedelta(days=7)
)
```

### Telemetry Ingestion

#### Send Telemetry Data

```python
from starlink_sdk import TelemetryIngestRequest, generate_idempotency_key

telemetry = TelemetryIngestRequest(
    terminal_id="TERMINAL_ID_123",
    timestamp=datetime.now(),
    metrics={
        "latency_ms": 45.2,
        "packet_loss_pct": 0.1,
        "downlink_mbps": 150.5,
        "uplink_mbps": 25.3,
        "signal_strength": -78.5
    }
)

response = client.telemetry.ingest(
    request=telemetry,
    idempotency_key=generate_idempotency_key()
)

print(f"Telemetry accepted: {response.accepted}")
print(f"Request ID: {response.request_id}")
```

### Pagination

For endpoints that return paginated results:

```python
from starlink_sdk import create_pagination_helper

# Manual pagination
terminals = client.terminals.list(limit=100)
while terminals.next_cursor:
    print(f"Processing {len(terminals.items)} terminals...")
    terminals = client.terminals.list(
        cursor=terminals.next_cursor,
        limit=100
    )

# Or use the pagination helper
paginator = create_pagination_helper(
    client.terminals, 
    'list', 
    status=TerminalStatus.ONLINE,
    limit=100
)

# Get all items (be careful with large datasets!)
all_terminals = paginator.get_all_items(max_pages=10)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from starlink_sdk import (
    StarlinkAPIError, 
    StarlinkClientError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError
)

try:
    terminal = await client.get_terminal_detail("INVALID_ID")
except NotFoundError:
    print("Terminal not found")
except AuthenticationError:
    print("Authentication failed - check your API secret")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Request validation failed: {e.detail}")
except StarlinkAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
except StarlinkClientError as e:
    print(f"Client error: {e.message}")
```

## Advanced Usage

### Custom HTTP Client

```python
import httpx

# Use custom HTTP client with specific settings
custom_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0),
    limits=httpx.Limits(max_connections=50)
)

async with StarlinkClient(client=custom_client) as client:
    # Use client as normal
    health = await client.get_fleet_health(...)
```

### Retry Configuration

```python
client = StarlinkClient(
    max_retries=5,  # Retry failed requests up to 5 times
    timeout=60.0    # 60 second timeout
)
```

### Raw API Access

```python
# Access the underlying HTTP client for custom requests
response = await client._make_request(
    'GET', 
    '/v1/custom-endpoint',
    params={'custom': 'parameter'}
)
data = response.json()
```

## Authentication Flow

The SDK implements an automatic token management system:

1. **Initial Authentication**: Uses your API secret to obtain an access token from `/v1/auth/token`
2. **Token Storage**: Keeps the token in memory with expiration tracking
3. **Automatic Refresh**: Refreshes tokens 30 seconds before expiration
4. **Retry Logic**: Automatically retries requests with fresh tokens on 401 errors

## Development

### Setup

```bash
git clone https://github.com/spacex/starlink-sdk
cd starlink-sdk
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact the SpaceX Developer Relations team or open an issue on GitHub.

## Changelog

### v0.1.0

- Initial release
- Full API coverage for Starlink Enterprise Dashboard
- Automatic token management
- Type-safe async client
- Comprehensive error handling
- Pagination support
