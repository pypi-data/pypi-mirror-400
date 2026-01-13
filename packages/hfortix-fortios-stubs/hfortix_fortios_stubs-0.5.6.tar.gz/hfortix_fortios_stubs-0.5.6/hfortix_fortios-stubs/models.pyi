"""
Type stubs for FortiOS Object Models

Provides type hints for zero-maintenance object wrappers for FortiOS API responses.
"""

from typing import Any, Generator, Literal, TypeVar, overload

_T = TypeVar("_T")

class FortiObject:
    """
    Zero-maintenance wrapper for FortiOS API responses.
    
    Provides clean attribute access to API response data with automatic
    flattening of member_table fields (lists of dicts with 'name' keys).
    
    Features:
    - No schemas required - works with any FortiOS version
    - No code generation - same class for all endpoints
    - No maintenance - automatically handles new fields
    - Auto-flattening of member_table fields for clean access
    - Escape hatch via get_full() for raw data access
    
    Examples:
        >>> # From dict response
        >>> data = {"name": "policy1", "srcaddr": [{"name": "addr1"}]}
        >>> obj = FortiObject(data)
        >>> 
        >>> # Clean attribute access
        >>> obj.name
        'policy1'
        >>> 
        >>> # Auto-flattened member_table fields
        >>> obj.srcaddr
        ['addr1']
        >>> 
        >>> # Get raw data when needed
        >>> obj.get_full('srcaddr')
        [{'name': 'addr1'}]
        >>> 
        >>> # Convert back to dict
        >>> obj.to_dict()
        {'name': 'policy1', 'srcaddr': [{'name': 'addr1'}]}
    
    Args:
        data: Dictionary from FortiOS API response
    """
    
    _data: dict[str, Any]
    
    def __init__(self, data: dict[str, Any]) -> None:
        """
        Initialize FortiObject with API response data.
        
        Args:
            data: Dictionary containing the API response fields
        """
        ...
    
    def __getattr__(self, name: str) -> Any:
        """
        Dynamic attribute access with automatic member_table flattening.
        
        For most FortiOS fields (strings, ints, etc.), returns the value as-is.
        For member_table fields (lists of dicts with 'name' key), automatically
        flattens to a list of name strings for cleaner access.
        
        Args:
            name: Attribute name to access
            
        Returns:
            Field value, with member_table fields auto-flattened
            
        Raises:
            AttributeError: If accessing private attributes (starting with '_')
            
        Examples:
            >>> obj.srcaddr  # Member table
            ['addr1', 'addr2']
            >>> obj.action  # Regular field
            'accept'
        """
        ...
    
    def get_full(self, name: str) -> Any:
        """
        Get raw field value without automatic processing.
        
        Use this when you need the full object structure from a member_table
        field instead of the auto-flattened name list.
        
        Args:
            name: Field name to retrieve
            
        Returns:
            Raw field value without any processing
            
        Examples:
            >>> obj.get_full('srcaddr')
            [{'name': 'addr1', 'q_origin_key': 'addr1'}]
        """
        ...
    
    def to_dict(self) -> dict[str, Any]:
        """
        Get the original dictionary data.
        
        Returns:
            Original API response dictionary
            
        Examples:
            >>> obj.to_dict()
            {'policyid': 1, 'name': 'policy1', ...}
        """
        ...
    
    def __repr__(self) -> str:
        """
        String representation of the object.
        
        Returns:
            String showing object type and identifier (name or policyid)
        """
        ...
    
    def __contains__(self, key: str) -> bool:
        """
        Check if field exists in the object.
        
        Args:
            key: Field name to check
            
        Returns:
            True if field exists, False otherwise
            
        Examples:
            >>> 'srcaddr' in obj
            True
        """
        ...
    
    def __len__(self) -> int:
        """
        Get number of fields in the object.
        
        Returns:
            Number of fields in the response data
            
        Examples:
            >>> len(obj)
            15
        """
        ...
    
    def keys(self) -> Any:
        """
        Get all field names.
        
        Returns:
            Dictionary keys view of all field names
            
        Examples:
            >>> list(obj.keys())
            ['policyid', 'name', 'srcaddr', 'dstaddr', ...]
        """
        ...
    
    def values(self) -> Generator[Any, None, None]:
        """
        Get all field values (processed).
        
        Note: This returns processed values (with auto-flattening).
        Use to_dict().values() for raw values.
        
        Returns:
            Generator of processed field values
        """
        ...
    
    def items(self) -> Generator[tuple[str, Any], None, None]:
        """
        Get all field name-value pairs (processed).
        
        Note: This returns processed values (with auto-flattening).
        Use to_dict().items() for raw values.
        
        Returns:
            Generator of (key, processed_value) tuples
        """
        ...
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get field value with optional default (dict-like interface).
        
        Args:
            key: Field name to retrieve
            default: Value to return if field doesn't exist
            
        Returns:
            Processed field value or default
            
        Examples:
            >>> obj.get('action', 'deny')
            'accept'
            >>> obj.get('nonexistent', 'default')
            'default'
        """
        ...

# Overloads for process_response to provide accurate return types
@overload
def process_response(
    result: list[dict[str, Any]],
    response_mode: Literal["object"],
    client: Any = None
) -> list[FortiObject]:
    """Process list response in object mode - returns list of FortiObjects."""
    ...

@overload
def process_response(
    result: list[dict[str, Any]],
    response_mode: Literal["dict"] | None,
    client: Any = None
) -> list[dict[str, Any]]:
    """Process list response in dict mode - returns list of dicts."""
    ...

@overload
def process_response(
    result: dict[str, Any],
    response_mode: Literal["object"],
    client: Any = None
) -> FortiObject | dict[str, Any]:
    """Process dict response in object mode - may return FortiObject or dict with wrapped results."""
    ...

@overload
def process_response(
    result: dict[str, Any],
    response_mode: Literal["dict"] | None,
    client: Any = None
) -> dict[str, Any]:
    """Process dict response in dict mode - returns dict as-is."""
    ...

def process_response(
    result: Any,
    response_mode: str | None,
    client: Any = None
) -> Any:
    """
    Process API response based on response_mode setting.
    
    Handles both raw_json=False (list of results) and raw_json=True (full response dict).
    
    Args:
        result: Raw API response (list or dict)
        response_mode: Response mode - "dict", "object", or None (use client default)
        client: HTTP client instance (to get default response_mode)
        
    Returns:
        Processed response - either dict/list or FortiObject/list[FortiObject]
        
    Examples:
        >>> # Dict mode with raw_json=False (default)
        >>> result = [{"name": "policy1", "srcaddr": [{"name": "addr1"}]}]
        >>> process_response(result, "dict")
        [{"name": "policy1", "srcaddr": [{"name": "addr1"}]}]
        
        >>> # Object mode with raw_json=False
        >>> objects = process_response(result, "object")
        >>> objects[0].name
        'policy1'
        >>> objects[0].srcaddr  # Auto-flattened!
        ['addr1']
        
        >>> # Object mode with raw_json=True
        >>> result = {'results': [{"name": "policy1", ...}], 'http_status': 200, ...}
        >>> response = process_response(result, "object")
        >>> response['results'][0].name  # Results are FortiObjects
        'policy1'
        >>> response['http_status']  # Metadata preserved
        200
    """
    ...
