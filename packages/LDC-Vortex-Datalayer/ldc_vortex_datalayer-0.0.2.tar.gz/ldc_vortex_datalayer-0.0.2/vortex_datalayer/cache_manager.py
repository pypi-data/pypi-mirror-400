"""
Cache Manager for Redis operations in repository layer.
Provides generic methods for caching operations with fallback to database.
"""

import json
import logging
from typing import Any, Optional, Callable
from functools import wraps

from . import redis_utils

logger = logging.getLogger('normal')


class CacheManager:
    """
    Cache Manager for Redis operations.
    Provides high-level caching methods using redis_utils for Redis operations.
    """
    
    @staticmethod
    def check_and_set_loan_creation_request(loan_id: str, ttl: int = 30) -> bool:
        """
        Check if a loan creation request is duplicate by checking Redis cache.
        If not duplicate, sets the cache key to mark the request as in-progress.
        
        Args:
            loan_id: The loan ID to check for duplicate request
            ttl: Time-to-live in seconds (default: 30 seconds)
            
        Returns:
            bool: True if duplicate request exists, False if this is a new request
        """
        try:
            cache_key = f"LOAN_CREATION_REQUEST:{loan_id}"
            
            # Check if key exists in Redis
            if redis_utils.exists(cache_key):
                logger.warning(f"Duplicate loan creation request detected for loan_id: {loan_id}")
                return True
            
            # Set the key with TTL to mark this request as in-progress
            redis_utils.set(cache_key, "1", ttl)
            logger.info(f"Loan creation request registered for loan_id: {loan_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking duplicate loan creation request for loan_id {loan_id}: {e}")
            # In case of Redis failure, allow the request to proceed (fail-open)
            return False
    
    @staticmethod
    def clear_loan_creation_request(loan_id: str) -> None:
        """
        Clear the loan creation request cache key.
        Should be called after successful loan creation or on error.
        
        Args:
            loan_id: The loan ID to clear from cache
        """
        try:
            cache_key = f"LOAN_CREATION_REQUEST:{loan_id}"
            redis_utils.delete(cache_key)
            logger.info(f"Loan creation request cache cleared for loan_id: {loan_id}")
        except Exception as e:
            logger.error(f"Error clearing loan creation request cache for loan_id {loan_id}: {e}")
    
    
    @staticmethod
    def get_or_set(
        cache_identifier: str,
        db_callback: Callable[[], Any],
        cache_key_prefix: Optional[str] = None,
        ttl: int = 1800,
        return_type: type = str
    ) -> Optional[Any]:
        """
        Generic cache get-or-set pattern with fallback to database.
        
        Args:
            cache_identifier: Unique identifier for the cache key
            db_callback: Function to call when cache miss occurs
            cache_key_prefix: Optional prefix for cache key (for logging/analysis)
            ttl: Time to live in seconds (default: 30 minutes)
            return_type: Expected return type for type conversion
            
        Returns:
            Cached or database result, None if not found
        """
        if not cache_identifier:
            logger.warning("Empty cache_identifier provided")
            return None
        
        # Build cache key
        if cache_key_prefix:
            cache_key = f"{cache_key_prefix}:{cache_identifier}"
        else:
            cache_key = cache_identifier
        
        try:
            # Check if Redis is available
            client = redis_utils.get_client()
            if not client:
                logger.warning("Redis client not available, falling back to DB")
                return db_callback()
            
            # Try to get from cache with type conversion
            try:
                result = redis_utils.get(cache_key, return_type)
                if result is not None:
                    # Log cache hit
                    log_data = {
                        "descr": "CACHE_OPERATION",
                        "cache_key_prefix": cache_key_prefix,
                        "cache_key": cache_key,
                        "cache_action": "HIT",
                        "data_type": return_type.__name__
                    }
                    logger.info(json.dumps(log_data))
                    return result
            except (ValueError, UnicodeDecodeError, TypeError, json.JSONDecodeError) as e:
                # Log invalid cache data
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "INVALID",
                    "data_type": return_type.__name__,
                    "error": str(e)
                }
                logger.warning(json.dumps(log_data))
                
                # Remove invalid cache entry
                try:
                    redis_utils.delete(cache_key)
                except Exception as delete_error:
                    logger.warning(f"Failed to delete invalid cache entry: {delete_error}")
            
            # Cache miss - fetch from database
            result = db_callback()
            
            if result is None:
                # Log no data found
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "NO_DATA_IN_DB",
                    "data_type": return_type.__name__
                }
                logger.info(json.dumps(log_data))
                return None
            
            # Store in cache
            try:
                redis_utils.set(cache_key, result, ttl)
                
                # Log cache set
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "SET",
                    "data_type": return_type.__name__
                }
                logger.info(json.dumps(log_data))
                
            except Exception as cache_error:
                # Log cache set failure
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "SET_FAILED",
                    "data_type": return_type.__name__,
                    "error": str(cache_error)
                }
                logger.warning(json.dumps(log_data))
                # Don't fail the operation if caching fails
            
            return result
            
        except Exception as e:
            # Log general error
            log_data = {
                "descr": "CACHE_OPERATION",
                "cache_key_prefix": cache_key_prefix,
                "cache_key": cache_key,
                "cache_action": "ERROR",
                "data_type": return_type.__name__,
                "error": str(e)
            }
            logger.error(json.dumps(log_data))
            
            # Fallback to database
            try:
                return db_callback()
            except Exception as db_error:
                logger.error(f"Database fallback also failed: {db_error}")
                return None
    
    @staticmethod
    def invalidate(cache_identifier: str, cache_key_prefix: Optional[str] = None) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            cache_identifier: Cache identifier to invalidate
            cache_key_prefix: Optional prefix for cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not cache_identifier:
            logger.warning("Empty cache_identifier provided for invalidation")
            return False
        
        cache_key = f"{cache_key_prefix}:{cache_identifier}" if cache_key_prefix else cache_identifier
        
        try:
            result = redis_utils.delete(cache_key)
            
            if result:
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "INVALIDATED"
                }
                logger.info(json.dumps(log_data))
            else:
                log_data = {
                    "descr": "CACHE_OPERATION",
                    "cache_key_prefix": cache_key_prefix,
                    "cache_key": cache_key,
                    "cache_action": "INVALIDATE_NOT_FOUND"
                }
                logger.info(json.dumps(log_data))
            return True
            
        except Exception as e:
            log_data = {
                "descr": "CACHE_OPERATION",
                "cache_key_prefix": cache_key_prefix,
                "cache_key": cache_key,
                "cache_action": "INVALIDATE_ERROR",
                "error": str(e)
            }
            logger.error(json.dumps(log_data))
            return False
    
    @staticmethod
    def get_stats(cache_key_prefix: Optional[str] = None) -> dict:
        """
        Get cache statistics for monitoring.
        
        Args:
            cache_key_prefix: Optional prefix to filter keys
            
        Returns:
            Dictionary with cache statistics
        """
        try:
            if cache_key_prefix:
                pattern = f"{cache_key_prefix}:*"
            else:
                pattern = "*"
            
            keys_list = redis_utils.keys(pattern)
            return {
                "total_keys": len(keys_list),
                "pattern": pattern,
                "keys_sample": [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys_list[:10]] if keys_list else []
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}


def cache_result(
    cache_identifier_func: Callable[[], str],
    cache_key_prefix: Optional[str] = None,
    ttl: int = 1800,
    return_type: type = str
):
    """
    Decorator for caching function results.
    
    Args:
        cache_identifier_func: Function that returns cache identifier
        cache_key_prefix: Optional prefix for cache key
        ttl: Time to live in seconds
        return_type: Expected return type
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_identifier = cache_identifier_func()
            return CacheManager.get_or_set(
                cache_identifier=cache_identifier,
                db_callback=lambda: func(*args, **kwargs),
                cache_key_prefix=cache_key_prefix,
                ttl=ttl,
                return_type=return_type
            )
        return wrapper
    return decorator
