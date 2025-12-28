"""
Starlink Enterprise Dashboard API SDK

A Python SDK for interacting with the Starlink Enterprise Dashboard API.
Features automatic authentication, token rotation, and type-safe API methods.

Example:
    ```python
    from starlink_sdk import StarlinkClient
    from datetime import datetime, timedelta
    
    # Simple synchronous usage - just like OpenAI
    client = StarlinkClient()
    
    # Get fleet health
    health = client.fleet.get_health(
        from_time=datetime.now() - timedelta(hours=1),
        to_time=datetime.now()
    )
    print(f"Healthy terminals: {health.counts.healthy}")
    
    # List terminals
    terminals = client.terminals.list(limit=50)
    for terminal in terminals.items:
        print(f"Terminal {terminal.terminal_id}: {terminal.status}")
    
    # Get terminal details
    terminal = client.terminals.get("TERMINAL_ID_123")
    print(f"Terminal health: {terminal.health_status}")
    
    # Get metrics
    metrics = client.terminals.get_metrics(
        terminal_id="TERMINAL_ID_123",
        from_time=datetime.now() - timedelta(hours=6),
        to_time=datetime.now(),
        metrics=["latency_ms", "downlink_mbps"]
    )
    
    # List alerts
    alerts = client.alerts.list(severity="critical")
    ```
"""

from .client import StarlinkClient, create_client
from .models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertsListResponse,
    FleetCounts,
    FleetHealthResponse,
    HealthFactor,
    HealthStatus,
    Interval,
    Location,
    MetricPoint,
    MetricsResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    TerminalDetail,
    TerminalListResponse,
    TerminalStatus,
    TerminalSummary,
    TopIssue,
)
from .exceptions import (
    StarlinkError,
    StarlinkAPIError,
    StarlinkClientError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    PermissionError,
)
from .utils import (
    generate_idempotency_key,
    now_utc,
    parse_datetime,
    format_datetime,
    validate_terminal_id,
    validate_metrics_list,
    create_pagination_helper,
)

__version__ = "0.1.0"
__author__ = "SpaceX"
__email__ = "dev@spacex.com"

__all__ = [
    # Main client
    "StarlinkClient",
    "create_client",
    
    # Models
    "Alert",
    "AlertSeverity", 
    "AlertStatus",
    "AlertsListResponse",
    "FleetCounts",
    "FleetHealthResponse",
    "HealthFactor",
    "HealthStatus",
    "Interval",
    "Location",
    "MetricPoint",
    "MetricsResponse",
    "TelemetryIngestRequest",
    "TelemetryIngestResponse",
    "TerminalDetail",
    "TerminalListResponse",
    "TerminalStatus",
    "TerminalSummary",
    "TopIssue",
    
    # Exceptions
    "StarlinkError",
    "StarlinkAPIError",
    "StarlinkClientError", 
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    
    # Utilities
    "generate_idempotency_key",
    "now_utc",
    "parse_datetime", 
    "format_datetime",
    "validate_terminal_id",
    "validate_metrics_list",
    "create_pagination_helper",
]