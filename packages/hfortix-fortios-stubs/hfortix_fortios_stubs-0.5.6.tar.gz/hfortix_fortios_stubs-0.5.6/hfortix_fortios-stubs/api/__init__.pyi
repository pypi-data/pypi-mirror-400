"""Type stubs for hfortix_fortios.api module."""

from __future__ import annotations

from hfortix_core.http.interface import IHTTPClient

from .utils import Utils
from .v2.cmdb import CMDB
from .v2.log import Log
from .v2.monitor import Monitor
from .v2.service import Service

__all__ = ["API"]

class API:
    """
    FortiOS REST API v2 Interface.
    
    Provides type-safe access to all FortiOS API endpoints.
    """
    
    cmdb: CMDB
    """Configuration Management Database - CRUD operations on configuration objects."""
    
    monitor: Monitor
    """Real-time monitoring and status data (read-only)."""
    
    log: Log
    """Historical log retrieval (read-only)."""
    
    service: Service
    """System services and operations."""
    
    utils: Utils
    """Utility functions for testing and diagnostics."""
    
    def __init__(self, client: IHTTPClient, vdom: str | None = None) -> None:
        """
        Initialize API interface.
        
        Args:
            client: HTTP client instance for API communication
            vdom: Virtual domain name (optional)
        """
        ...
