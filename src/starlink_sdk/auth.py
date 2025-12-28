"""Authentication handler for the Starlink Enterprise Dashboard API."""

import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from .models import TokenResponse


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""
    pass


class TokenManager:
    """Manages authentication tokens with automatic rotation."""
    
    def __init__(
        self, 
        base_url: str, 
        api_secret: Optional[str] = None,
        session: Optional[requests.Session] = None
    ):
        """
        Initialize the token manager.
        
        Args:
            base_url: Base URL for the API
            api_secret: API secret for authentication (if None, reads from STARLINK_API_SECRET)
            session: HTTP session to use (if None, creates a new one)
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret = api_secret or os.getenv('STARLINK_API_SECRET')
        if not self.api_secret:
            raise AuthenticationError("API secret not provided. Set STARLINK_API_SECRET environment variable or pass api_secret parameter.")
        
        self.session = session or requests.Session()
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._refresh_lock = threading.Lock()
    
    def get_token(self) -> str:
        print(f"Getting token for base URL: {self.base_url}")
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        if self._is_token_valid():
            return self._token
        
        with self._refresh_lock:
            # Check again in case another thread already refreshed
            if self._is_token_valid():
                return self._token
            
            self._refresh_token()
            return self._token
    
    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._token or not self._token_expires_at:
            return False
        
        # Add 30 second buffer before expiration
        return datetime.now(timezone.utc) < (self._token_expires_at - timedelta(seconds=30))
    
    def _refresh_token(self) -> None:
        print(f"Refreshing token for base URL: {self.base_url}")
        """Refresh the authentication token."""
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/token",
                json={"api_secret": self.api_secret},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            token_data = TokenResponse(**response.json())
            self._token = token_data.access_token
            
            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.expires_in)
            self._token_expires_at = expires_at
            
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API secret") from e
            elif e.response.status_code == 403:
                raise AuthenticationError("API secret not authorized") from e
            else:
                raise AuthenticationError(f"Token refresh failed: {e.response.status_code}") from e
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}") from e
    
    def get_auth_header(self) -> dict[str, str]:
        """Get authorization header with valid token."""
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}
