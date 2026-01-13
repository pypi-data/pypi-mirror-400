"""
Helper functions for master account caching operations.
Separates Redis caching logic from SQL operations.
"""

import logging
from typing import Optional, Dict, Any

from .. import redis_utils
from ..entity.account import Account
from ..entity.master_account import MasterAccount

logger = logging.getLogger('normal')


def get_master_account_id(account_name: str) -> Optional[Dict[str, Any]]:
    """
    Get master account id by account name with Redis caching.
    Fetches from Redis first, if not available fetches from DB and caches it.
    
    Uses Account entity's fetch_master_account_type_id_by_account_name method.

    Args:
        account_name: The name of the ledger master account

    Returns:
        Dict with account_type_id and account_id, or None if not found
    """
    cache_key = f"MASTER_ACCOUNT_ID:{account_name}"
    
    # Try to get from Redis cache
    try:
        cached_result = redis_utils.get(cache_key, dict)
        if cached_result:
            logger.debug(f"Cache hit for master account: {account_name}")
            return cached_result
    except Exception as e:
        logger.warning(f"Redis get failed for {cache_key}: {e}")
    
    # Fetch from database
    logger.debug(f"Cache miss for master account: {account_name}, fetching from DB")
    account = Account()
    result = account.fetch_master_account_type_id_by_account_name(account_name)
    
    # Cache the result if found
    if result:
        try:
            redis_utils.set(cache_key, result)
            logger.debug(f"Cached master account data for: {account_name}")
        except Exception as e:
            logger.warning(f"Redis set failed for {cache_key}: {e}")
    
    return result


def get_master_account_type_id(account_name: str) -> Optional[Dict[str, Any]]:
    """
    Get master account type id by account name with Redis caching.
    Fetches from Redis first, if not available fetches from DB and caches it.
    
    Uses MasterAccount entity's get_account_by_name method.

    Args:
        account_name: The name of the ledger master account

    Returns:
        Dict with id, or None if not found
    """
    cache_key = f"MASTER_ACCOUNT_TYPE_ID:{account_name}"
    
    # Try to get from Redis cache
    try:
        cached_result = redis_utils.get(cache_key, dict)
        if cached_result:
            logger.debug(f"Cache hit for master account: {account_name}")
            return cached_result
    except Exception as e:
        logger.warning(f"Redis get failed for {cache_key}: {e}")
    
    # Fetch from database
    logger.debug(f"Cache miss for master account: {account_name}, fetching from DB")
    master_account = MasterAccount()
    result = master_account.get_account_by_name(account_name)
    
    # Cache the result if found
    if result:
        try:
            redis_utils.set(cache_key, result)
            logger.debug(f"Cached master account data for: {account_name}")
        except Exception as e:
            logger.warning(f"Redis set failed for {cache_key}: {e}")
    
    return result
