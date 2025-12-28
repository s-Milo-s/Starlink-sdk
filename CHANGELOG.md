# Changelog

All notable changes to the Starlink SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-27

### Added

#### Core Features
- **StarlinkClient**: Async-first client with automatic token management
- **Authentication**: JWT token handling with automatic rotation
- **Type Safety**: Full type hints and Pydantic models for all API responses
- **Error Handling**: Comprehensive exception hierarchy for different error types
- **Retry Logic**: Configurable retry mechanism for failed requests
- **Pagination**: Helper utilities for handling paginated API responses

#### API Coverage
- **Fleet Health**: Get aggregate health statistics and top issues
- **Terminal Management**: List, filter, and get detailed terminal information
- **Metrics**: Time-series data retrieval with configurable intervals
- **Alerts**: Alert management with filtering and status tracking
- **Telemetry**: Ingest telemetry data with idempotency support

#### Models
- `Alert`, `AlertSeverity`, `AlertStatus` - Alert management
- `FleetHealthResponse`, `FleetCounts` - Fleet health monitoring  
- `TerminalDetail`, `TerminalSummary`, `TerminalStatus` - Terminal information
- `MetricsResponse`, `MetricPoint`, `Interval` - Time-series metrics
- `TelemetryIngestRequest`, `TelemetryIngestResponse` - Telemetry ingestion
- `HealthStatus`, `HealthFactor`, `Location` - Health and location data

#### Utilities
- `generate_idempotency_key()` - UUID-based idempotency key generation
- `validate_terminal_id()` - Terminal ID format validation
- `validate_metrics_list()` - Metrics name validation
- `PaginationHelper` - Automated pagination handling
- `create_pagination_helper()` - Convenience function for pagination

#### Examples
- **Basic Fleet Health**: Simple fleet monitoring example
- **Terminal Management**: Terminal listing, details, and metrics
- **Alerts and Telemetry**: Alert handling and telemetry ingestion
- **Advanced Usage**: Error handling, batching, and custom configuration

#### Configuration
- Environment-based configuration (`STARLINK_API_SECRET`, `STARLINK_BASE_URL`)
- Custom HTTP client support with `httpx`
- Configurable timeouts and retry limits
- Development setup scripts and examples

### Authentication Flow
- Automatic token acquisition from `/v1/auth/token` endpoint
- Token refresh 30 seconds before expiration
- Automatic retry with fresh tokens on 401 errors
- Support for custom API secrets and base URLs

### Dependencies
- `httpx>=0.24.0` - Async HTTP client
- `pydantic>=2.0.0` - Data validation and serialization
- `python-dateutil>=2.8.0` - Enhanced datetime handling

### Development Tools
- `pytest` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking
- Development setup script (`setup_dev.py`)

## [Unreleased]

### Planned
- Synchronous client option
- Response caching
- Websocket support for real-time updates
- Additional metrics and health indicators
- Performance optimizations
- CLI tools for common operations
