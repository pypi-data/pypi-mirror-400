"""
Redis Utilities

Centralized Redis connection and operations for the repository layer.
All Redis operations should go through this module.
"""

import json
import logging
from typing import Any, Optional, List, Type

import redis
from django.conf import settings

logger = logging.getLogger('normal')

# Singleton Redis client
_client = None


def get_client():
    """
    Get singleton Redis client instance.
    
    Returns:
        redis.StrictRedis: A Redis client instance, or None if connection fails
    """
    global _client
    if _client is None:
        _client = redis.StrictRedis.from_url(
            settings.IOS_REDIS_CACHE,
            decode_responses=False
        )
        _client.ping()
    return _client


def get(key: str, return_type: Optional[Type] = None) -> Optional[Any]:
    """
    Get value from Redis.
    
    Args:
        key: Redis key to retrieve
        return_type: Expected return type (str, int, float, bool, dict, list).
                     If None, returns raw bytes (backward compatible).
        
    Returns:
        Value converted to return_type, or raw bytes if return_type is None.
        Returns None if key not found.
    """
    client = get_client()
    if not client:
        return None
    
    cached_data = client.get(key)
    if cached_data is None:
        return None
    
    # Return raw bytes if no type specified (backward compatible)
    if return_type is None:
        return cached_data
    
    # Decode once for all typed conversions
    decoded = cached_data.decode('utf-8')
    
    # Handle type conversions
    if return_type == str:
        return decoded
    if return_type == bool:
        return decoded.lower() == 'true'
    if return_type in (int, float):
        return return_type(decoded)
    # Complex types (dict, list) - JSON parse
    return json.loads(decoded)


def set(key: str, value: Any, ttl: int = 1800) -> bool:
    """
    Set value in Redis with TTL.
    Automatically serializes complex types to JSON.
    
    Args:
        key: Redis key
        value: Value to store (strings/bytes stored as-is, complex types JSON serialized)
        ttl: Time to live in seconds (default: 30 minutes)
        
    Returns:
        True if successful
    """
    client = get_client()
    if not client:
        return False
    
    # Serialize value for storage
    if isinstance(value, bytes):
        cache_data = value
    elif isinstance(value, (dict, list)):
        cache_data = json.dumps(value)
    elif isinstance(value, str):
        cache_data = value
    else:
        cache_data = str(value)
    
    client.setex(name=key, time=ttl, value=cache_data)
    return True


def delete(key: str) -> bool:
    """
    Delete key from Redis.
    
    Args:
        key: Redis key to delete
        
    Returns:
        True if key was deleted, False if key didn't exist
    """
    client = get_client()
    if not client:
        return False
    return client.delete(key) > 0


def exists(key: str) -> bool:
    """
    Check if key exists in Redis.
    
    Args:
        key: Redis key to check
        
    Returns:
        True if key exists, False otherwise
    """
    client = get_client()
    if not client:
        return False
    return client.exists(key) > 0


def keys(pattern: str) -> List[bytes]:
    """
    Get keys matching pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "prefix:*")
        
    Returns:
        List of matching keys as bytes
    """
    client = get_client()
    if not client:
        return []
    return client.keys(pattern)
