"""Main client for the Starlink Enterprise Dashboard API."""

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
    FleetHealthResponse,
    Interval,
    MetricsResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    TerminalDetail,
    TerminalListResponse,
    TerminalStatus,
)


class StarlinkClient:
    """
    Synchronous client for the Starlink Enterprise Dashboard API.
    
    Features:
    - Automatic token management and rotation
    - Type-safe API methods
    - Configurable base URL and authentication
    - Comprehensive error handling
    
    Usage:
        from starlink_sdk import StarlinkClient
        
        client = StarlinkClient()
        health = client.fleet.get_health(from_time=..., to_time=...)
        terminals = client.terminals.list()
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        """
        Initialize the Starlink client.
        
        Args:
            base_url: API base URL (defaults to STARLINK_BASE_URL env var or demo URL)
            api_secret: API secret (defaults to STARLINK_API_SECRET env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            session: Custom HTTP session (optional)
        """
        self.base_url = (
            base_url 
            or os.getenv('STARLINK_BASE_URL') 
            or 'https://starlink-enterprise-api.spacex.com'
        ).rstrip('/')
        
        # Create HTTP session if not provided
        if session is None:
            self.session = requests.Session()
            self.session.timeout = timeout
            self._owns_session = True
        else:
            self.session = session
            self._owns_session = False
        
        # Initialize token manager
        self.token_manager = TokenManager(
            base_url=self.base_url,
            api_secret=api_secret,
            session=self.session
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
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Get authentication header
        auth_header = self.token_manager.get_auth_header()
        
        # Merge headers
        request_headers = {**auth_header}
        if headers:
            request_headers.update(headers)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=request_headers
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
    
    def get(self, terminal_id: str) -> TerminalDetail:
        """
        Get detailed information about a terminal.
        
        Args:
            terminal_id: Terminal identifier
            
        Returns:
            Terminal detail response
        """
        response = self.client._make_request('GET', f'/v1/terminals/{terminal_id}')
        return TerminalDetail(**response.json())
    
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
    base_url: Optional[str] = None,
    api_secret: Optional[str] = None,
    **kwargs
) -> StarlinkClient:
    """
    Create and return a configured Starlink client.
    
    Args:
        base_url: API base URL
        api_secret: API secret
        **kwargs: Additional client options
        
    Returns:
        Configured client instance
    """
    return StarlinkClient(base_url=base_url, api_secret=api_secret, **kwargs)