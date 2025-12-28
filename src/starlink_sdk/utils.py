"""Utility functions for the Starlink SDK."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .models import AlertSeverity, AlertStatus, HealthStatus, Interval, TerminalStatus


def generate_idempotency_key() -> str:
    """
    Generate a unique idempotency key for API requests.
    
    Returns:
        UUID-based idempotency key
    """
    return str(uuid.uuid4())


def now_utc() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def parse_datetime(dt: Union[str, datetime]) -> datetime:
    """
    Parse datetime from string or pass through datetime object.
    
    Args:
        dt: Datetime string or datetime object
        
    Returns:
        Parsed datetime object
    """
    if isinstance(dt, str):
        return datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt


def format_datetime(dt: datetime) -> str:
    """
    Format datetime for API requests.
    
    Args:
        dt: Datetime to format
        
    Returns:
        ISO formatted datetime string
    """
    return dt.isoformat()


def validate_terminal_id(terminal_id: str) -> bool:
    """
    Validate terminal ID format.
    
    Args:
        terminal_id: Terminal ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - adjust based on actual terminal ID format
    return (
        isinstance(terminal_id, str) 
        and len(terminal_id) > 0 
        and len(terminal_id) <= 64
        and terminal_id.replace('-', '').replace('_', '').isalnum()
    )


def validate_metrics_list(metrics: List[str]) -> bool:
    """
    Validate list of metric names.
    
    Args:
        metrics: List of metric names
        
    Returns:
        True if valid, False otherwise
    """
    valid_metrics = {
        'latency_ms',
        'packet_loss_pct', 
        'uptime_pct',
        'downlink_mbps',
        'uplink_mbps'
    }
    
    return all(metric in valid_metrics for metric in metrics)


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from dictionary.
    
    Args:
        data: Dictionary to filter
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if v is not None}


def build_query_params(
    status: Optional[Union[str, TerminalStatus]] = None,
    severity: Optional[Union[str, AlertSeverity]] = None,
    alert_status: Optional[Union[str, AlertStatus]] = None,
    health_status: Optional[Union[str, HealthStatus]] = None,
    interval: Optional[Union[str, Interval]] = None,
    terminal_id: Optional[str] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, str]:
    """
    Build query parameters dictionary for API requests.
    
    Args:
        status: Terminal status filter
        severity: Alert severity filter
        alert_status: Alert status filter
        health_status: Health status filter
        interval: Metrics interval
        terminal_id: Terminal ID filter
        from_time: Start time filter
        to_time: End time filter
        limit: Result limit
        cursor: Pagination cursor
        metrics: List of metrics to retrieve
        **kwargs: Additional parameters
        
    Returns:
        Query parameters dictionary
    """
    params: Dict[str, str] = {}
    
    if status:
        params['status'] = status if isinstance(status, str) else status.value
    
    if severity:
        params['severity'] = severity if isinstance(severity, str) else severity.value
    
    if alert_status:
        params['status'] = alert_status if isinstance(alert_status, str) else alert_status.value
    
    if health_status:
        params['health_status'] = health_status if isinstance(health_status, str) else health_status.value
    
    if interval:
        params['interval'] = interval if isinstance(interval, str) else interval.value
    
    if terminal_id:
        params['terminal_id'] = terminal_id
    
    if from_time:
        params['from'] = format_datetime(from_time)
    
    if to_time:
        params['to'] = format_datetime(to_time)
    
    if limit is not None:
        params['limit'] = str(min(max(limit, 1), 500))
    
    if cursor:
        params['cursor'] = cursor
    
    if metrics:
        params['metrics'] = ','.join(metrics)
    
    # Add any additional parameters
    for key, value in kwargs.items():
        if value is not None:
            params[key] = str(value)
    
    return params


class PaginationHelper:
    """Helper class for handling paginated API responses."""
    
    def __init__(self, client, method_name: str, **base_params):
        """
        Initialize pagination helper.
        
        Args:
            client: Starlink client instance
            method_name: Name of the client method to call
            **base_params: Base parameters for the method
        """
        self.client = client
        self.method_name = method_name
        self.base_params = base_params
        self.next_cursor: Optional[str] = None
        self.has_more = True
    
    def get_next_page(self):
        """
        Get the next page of results.
        
        Returns:
            Next page response
        """
        if not self.has_more:
            return None
        
        params = self.base_params.copy()
        if self.next_cursor:
            params['cursor'] = self.next_cursor
        
        method = getattr(self.client, self.method_name)
        response = method(**params)
        
        self.next_cursor = response.next_cursor
        self.has_more = bool(self.next_cursor)
        
        return response
    
    def get_all_items(self, max_pages: Optional[int] = None):
        """
        Get all items across all pages.
        
        Args:
            max_pages: Maximum number of pages to fetch (None for unlimited)
            
        Returns:
            List of all items
        """
        all_items = []
        page_count = 0
        
        while self.has_more:
            if max_pages and page_count >= max_pages:
                break
            
            response = self.get_next_page()
            if response:
                all_items.extend(response.items)
                page_count += 1
            else:
                break
        
        return all_items


def create_pagination_helper(client, method_name: str, **params) -> PaginationHelper:
    """
    Create a pagination helper for a specific method.
    
    Args:
        client: Starlink client instance
        method_name: Name of the method to paginate
        **params: Parameters for the method
        
    Returns:
        Configured pagination helper
    """
    return PaginationHelper(client, method_name, **params)
