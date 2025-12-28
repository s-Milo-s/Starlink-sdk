"""Main client for the Starlink Enterprise Dashboard API."""

import json
import os
from datetime import datetime
from typing import List, Optional, Union
from urllib.parse import urlencode

import requests

from .auth import TokenManager
from .exceptions import StarlinkAPIError, StarlinkClientError
from .models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertsListResponse,
    AlertUpdateRequest,
    AlertUpdateResponse,
    FleetHealthResponse,
    Interval,
    MetricsResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    TerminalSummary,
    TerminalListResponse,
    TerminalStatus,
)


class StarlinkClient:
    """
    Synchronous client for the Starlink Enterprise Dashboard API.
    
    Features:
    - Automatic token management and rotation
    - Type-safe API methods
    - Environment-based URL configuration
    - Comprehensive error handling
    - Stateless HTTP requests for backend-to-backend communication
    
    Usage:
        from starlink_sdk import StarlinkClient
        
        # Use environment name
        client = StarlinkClient(environment="production")
        # or
        client = StarlinkClient(environment="staging")
        # or
        client = StarlinkClient()  # defaults to production
        
        health = client.fleet.get_health(from_time=..., to_time=...)
        terminals = client.terminals.list()
    """
    
    # Environment URL mappings
    ENVIRONMENT_URLS = {
        'production': 'https://starlink-enterprise-api.spacex.com',
        'staging': 'https://staging-starlink-enterprise-api.spacex.com',
        'development': 'http://starlink-api:8000',
        'demo': 'http://localhost:8000',
        'local': 'http://localhost:8000',
    }
    
    def __init__(
        self,
        environment: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize the Starlink client.
        
        Args:
            environment: Environment name (production, staging, development, demo, local)
                        Defaults to STARLINK_ENVIRONMENT env var or 'production'
            api_secret: API secret (defaults to STARLINK_API_SECRET env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Determine environment
        env = (
            environment 
            or os.getenv('STARLINK_ENVIRONMENT') 
            or 'production'
        ).lower()
        
        # Get base URL from environment mapping
        if env not in self.ENVIRONMENT_URLS:
            raise ValueError(
                f"Invalid environment '{env}'. "
                f"Must be one of: {', '.join(self.ENVIRONMENT_URLS.keys())}"
            )
        
        self.environment = env
        self.base_url = self.ENVIRONMENT_URLS[env].rstrip('/')
        self.timeout = timeout
        print(f"Using Starlink API base URL: {self.base_url}")
        
        # Initialize token manager
        self.token_manager = TokenManager(
            base_url=self.base_url,
            api_secret=api_secret,
            timeout=timeout
        )
        
        self.max_retries = max_retries
        
        # Initialize API namespaces
        self.fleet = FleetAPI(self)
        self.terminals = TerminalsAPI(self)
        self.alerts = AlertsAPI(self)
        self.telemetry = TelemetryAPI(self)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """
        Make an authenticated HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json: JSON body
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            StarlinkAPIError: For API-specific errors
            StarlinkClientError: For client-side errors
        """
        print(f"Making {method} request to endpoint: {endpoint}")
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Get authentication header
        auth_header = self.token_manager.get_auth_header()
        
        # Merge headers
        request_headers = {**auth_header}
        if headers:
            request_headers.update(headers)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                # Check for success
                if response.ok:
                    return response
                
                # Handle specific error codes
                if response.status_code == 401:
                    # Token might be expired, let token manager handle refresh
                    auth_header = self.token_manager.get_auth_header()
                    request_headers.update(auth_header)
                    continue
                
                # Raise for other HTTP errors
                response.raise_for_status()
                
            except requests.HTTPError as e:
                error_detail = None
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
                
                raise StarlinkAPIError(
                    f"API request failed: {e.response.status_code}",
                    status_code=e.response.status_code,
                    detail=error_detail
                ) from e
            
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    raise StarlinkClientError(f"Request failed after {self.max_retries} retries: {str(e)}") from e
                # Continue to retry
        
        raise StarlinkClientError(f"Request failed after {self.max_retries} retries")
    
    def health_check(self) -> dict:
        """
        Check API health status.
        
        Returns:
            Health check response
        """
        response = self._make_request('GET', '/health')
        return response.json()
    
    def get_api_info(self) -> dict:
        """
        Get basic API information.
        
        Returns:
            API information
        """
        response = self._make_request('GET', '/')
        return response.json()


class FleetAPI:
    """Fleet management API methods."""
    
    def __init__(self, client: StarlinkClient):
        self.client = client
    
    def get_health(
        self, 
        from_time: datetime, 
        to_time: datetime
    ) -> FleetHealthResponse:
        """
        Get fleet health summary.
        
        Args:
            from_time: Start time for health summary
            to_time: End time for health summary
            
        Returns:
            Fleet health response
        """
        params = {
            'from': from_time.isoformat(),
            'to': to_time.isoformat()
        }
        
        response = self.client._make_request('GET', '/v1/fleet/health', params=params)
        return FleetHealthResponse(**response.json())


class TerminalsAPI:
    """Terminal management API methods."""
    
    def __init__(self, client: StarlinkClient):
        self.client = client
    
    def list(
        self,
        status: Optional[Union[TerminalStatus, str]] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> TerminalListResponse:
        """
        List terminals for an account.
        
        Args:
            status: Filter by terminal status
            limit: Maximum number of results (1-500)
            cursor: Pagination cursor
            
        Returns:
            Terminal list response
        """
        params = {'limit': min(max(limit, 1), 500)}
        
        if status:
            params['status'] = status if isinstance(status, str) else status.value
        if cursor:
            params['cursor'] = cursor
        
        response = self.client._make_request('GET', '/v1/terminals', params=params)
        return TerminalListResponse(**response.json())
    
    def get(self, terminal_id: str) -> TerminalSummary:
        """
        Get detailed information about a terminal.
        
        Args:
            terminal_id: Terminal identifier
            
        Returns:
            Terminal summary response
        """
        response = self.client._make_request('GET', f'/v1/terminals/{terminal_id}')
        return TerminalSummary(**response.json())
    
    def get_metrics(
        self,
        terminal_id: str,
        from_time: datetime,
        to_time: datetime,
        interval: Union[Interval, str] = Interval.FIVE_MINUTES,
        metrics: Optional[List[str]] = None
    ) -> MetricsResponse:
        """
        Get time-series metrics for a terminal.
        
        Args:
            terminal_id: Terminal identifier
            from_time: Start time (inclusive)
            to_time: End time (exclusive)
            interval: Aggregation interval
            metrics: List of metric keys to retrieve
            
        Returns:
            Metrics response
        """
        params = {
            'from': from_time.isoformat(),
            'to': to_time.isoformat(),
            'interval': interval if isinstance(interval, str) else interval.value
        }
        
        if metrics:
            params['metrics'] = ','.join(metrics)
        
        response = self.client._make_request('GET', f'/v1/terminals/{terminal_id}/metrics', params=params)
        return MetricsResponse(**response.json())


class AlertsAPI:
    """Alert management API methods."""
    
    def __init__(self, client: StarlinkClient):
        self.client = client
    
    def list(
        self,
        status: Union[AlertStatus, str] = AlertStatus.OPEN,
        severity: Optional[Union[AlertSeverity, str]] = None,
        terminal_id: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> AlertsListResponse:
        """
        List alerts with filtering options.
        
        Args:
            status: Filter by alert status
            severity: Filter by severity
            terminal_id: Filter by terminal
            from_time: Filter by creation time (start)
            to_time: Filter by creation time (end)
            limit: Maximum number of results (1-500)
            cursor: Pagination cursor
            
        Returns:
            Alerts list response
        """
        params = {
            'status': status if isinstance(status, str) else status.value,
            'limit': min(max(limit, 1), 500)
        }
        
        if severity:
            params['severity'] = severity if isinstance(severity, str) else severity.value
        if terminal_id:
            params['terminal_id'] = terminal_id
        if from_time:
            params['from'] = from_time.isoformat()
        if to_time:
            params['to'] = to_time.isoformat()
        if cursor:
            params['cursor'] = cursor
        
        response = self.client._make_request('GET', '/v1/alerts', params=params)
        return AlertsListResponse(**response.json())
    
    def update(
        self,
        alert_id: str,
        update_request: str,
        idempotency_key: Optional[str] = None
    ) -> AlertUpdateResponse:
        """
        Update an alert's status.
        
        Args:
            alert_id: Alert identifier
            update_request: JSON string containing update data (e.g., '{"status": "acknowledged"}')
            idempotency_key: Optional idempotency key for request deduplication
            
        Returns:
            Alert update response
            
        Example:
            response = client.alerts.update(
                "alert_123", 
                '{"status": "acknowledged"}',
                idempotency_key="unique_key_456"
            )
        """
        try:
            # Parse JSON string to dictionary
            update_data = json.loads(update_request)
            
            # Validate the data by creating AlertUpdateRequest instance
            validated_request = AlertUpdateRequest(**update_data)
            
        except json.JSONDecodeError as e:
            raise StarlinkClientError(f"Invalid JSON in update_request: {e}")
        except Exception as e:
            raise StarlinkClientError(f"Invalid update_request data: {e}")
        
        headers = {}
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        
        response = self.client._make_request(
            'PATCH', 
            f'/v1/alerts/{alert_id}',
            json=update_data,
            headers=headers if headers else None
        )
        return AlertUpdateResponse(**response.json())


class TelemetryAPI:
    """Telemetry ingestion API methods."""
    
    def __init__(self, client: StarlinkClient):
        self.client = client
    
    def ingest(
        self,
        request: TelemetryIngestRequest,
        idempotency_key: str
    ) -> TelemetryIngestResponse:
        """
        Ingest telemetry data for a terminal.
        
        Args:
            request: Telemetry ingest request
            idempotency_key: Unique key for request idempotency
            
        Returns:
            Telemetry ingest response
        """
        headers = {'Idempotency-Key': idempotency_key}
        
        response = self.client._make_request(
            'POST', 
            '/v1/telemetry', 
            json=request.model_dump(mode='json'),
            headers=headers
        )
        return TelemetryIngestResponse(**response.json())


# Convenience function for creating a client
def create_client(
    environment: Optional[str] = None,
    api_secret: Optional[str] = None,
    **kwargs
) -> StarlinkClient:
    """
    Create and return a configured Starlink client.
    
    Args:
        environment: Environment name (production, staging, development, demo, local)
        api_secret: API secret
        **kwargs: Additional client options
        
    Returns:
        Configured client instance
    """
    return StarlinkClient(environment=environment, api_secret=api_secret, **kwargs)