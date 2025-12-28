"""Data models for the Starlink Enterprise Dashboard API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status values."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class HealthStatus(str, Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class TerminalStatus(str, Enum):
    """Terminal status values."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class Interval(str, Enum):
    """Time interval values for metrics."""
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    ONE_HOUR = "1h"


class Location(BaseModel):
    """Geographic location information."""
    label: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class HealthFactor(BaseModel):
    """Health factor contributing to terminal status."""
    factor: str
    value: float
    threshold: float
    message: str


class Alert(BaseModel):
    """Alert information."""
    alert_id: str
    terminal_id: str
    severity: AlertSeverity
    type: str
    message: str
    created_at: datetime
    status: AlertStatus


class AlertsListResponse(BaseModel):
    """Response for listing alerts."""
    items: List[Alert]
    next_cursor: Optional[str] = None


class FleetCounts(BaseModel):
    """Fleet health counts."""
    healthy: int
    degraded: int
    offline: int


class TopIssue(BaseModel):
    """Top issue affecting the fleet."""
    type: str
    count: int
    message: str


class FleetHealthResponse(BaseModel):
    """Fleet health summary response."""
    from_time: datetime
    to_time: datetime
    counts: FleetCounts
    top_issues: Optional[List[TopIssue]] = None


class TerminalSummary(BaseModel):
    """Terminal summary information."""
    terminal_id: str
    health_status: HealthStatus
    last_seen: datetime
    status: TerminalStatus
    name: Optional[str] = None
    location: Optional[Location] = None


class TerminalListResponse(BaseModel):
    """Response for listing terminals."""
    items: List[TerminalSummary]
    next_cursor: Optional[str] = None


class TerminalDetail(BaseModel):
    """Detailed terminal information."""
    terminal_id: str
    health_status: HealthStatus
    last_seen: datetime
    status: TerminalStatus
    name: Optional[str] = None
    location: Optional[Location] = None
    account_id: Optional[str] = None
    firmware_version: Optional[str] = None
    health_factors: Optional[List[HealthFactor]] = None


class MetricPoint(BaseModel):
    """Single metric data point."""
    t: datetime = Field(description="Timestamp")
    v: float = Field(description="Value")


class MetricsResponse(BaseModel):
    """Metrics response for a terminal."""
    terminal_id: str
    from_time: datetime
    to_time: datetime
    interval: Interval
    series: Dict[str, List[MetricPoint]]


class TelemetryIngestRequest(BaseModel):
    """Request to ingest telemetry data."""
    terminal_id: str
    timestamp: datetime
    metrics: Dict[str, Any]


class TelemetryIngestResponse(BaseModel):
    """Response from telemetry ingestion."""
    request_id: str
    accepted: bool


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    expires_at: Optional[datetime] = None


class ValidationError(BaseModel):
    """Validation error details."""
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """HTTP validation error response."""
    detail: List[ValidationError]


class AlertUpdateRequest(BaseModel):
    """Request model for updating alert status."""
    status: AlertStatus


class AlertUpdateResponse(BaseModel):
    """Response model for alert update."""
    alert_id: str
    terminal_id: str
    severity: AlertSeverity
    type: str
    message: str
    created_at: datetime
    status: AlertStatus
    updated_at: datetime
