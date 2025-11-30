"""
Blob Storage Cache Utilities for Azure Functions

This module provides caching functionality using Azure Blob Storage to reduce
CosmosDB query load. Implements time-based cache expiration with graceful
degradation on errors.

Usage:
    from shared_code.cache_utils import get_cached_data, save_cached_data, invalidate_cache

    # Try to get cached data
    cached = get_cached_data(blob_container, 'posts')
    if cached:
        return cached

    # Query database and cache result
    data = query_cosmosdb()
    save_cached_data(blob_container, 'posts', data)
    return data
"""

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceNotFoundError, AzureError
from datetime import datetime, timezone, timedelta
import json
import logging

# Cache configuration
CACHE_FOLDER = "cache"
DEFAULT_TTL_SECONDS = 900  # 15 minutes


def get_cached_data(blob_container, cache_key, ttl_seconds=DEFAULT_TTL_SECONDS):
    """
    Retrieve cached data from blob storage if it exists and is fresh.

    Args:
        blob_container: Azure Blob ContainerClient instance
        cache_key: Cache key (e.g., 'posts', 'comments-0001')
        ttl_seconds: Time-to-live in seconds (default: 900 = 15 minutes)

    Returns:
        Cached data (dict/list) if cache hit and fresh, None otherwise

    Raises:
        No exceptions raised - returns None on any error for graceful degradation
    """
    try:
        blob_name = f"{CACHE_FOLDER}/{cache_key}.json"
        blob_client = blob_container.get_blob_client(blob_name)

        # Check if blob exists and get properties
        blob_props = blob_client.get_blob_properties()

        # Check if cache is still fresh
        cache_age = datetime.now(timezone.utc) - blob_props.last_modified
        if cache_age < timedelta(seconds=ttl_seconds):
            # Cache hit - retrieve data
            blob_data = blob_client.download_blob().readall()
            cached_content = json.loads(blob_data)

            logging.info(f"Cache HIT: {cache_key} (age: {cache_age.total_seconds():.1f}s)")
            return cached_content.get('data')
        else:
            # Cache expired
            logging.info(f"Cache EXPIRED: {cache_key} (age: {cache_age.total_seconds():.1f}s, TTL: {ttl_seconds}s)")
            return None

    except ResourceNotFoundError:
        # Cache miss - blob doesn't exist
        logging.info(f"Cache MISS: {cache_key} (blob not found)")
        return None
    except json.JSONDecodeError as e:
        # Invalid JSON in cache - treat as cache miss and clean up
        logging.warning(f"Cache CORRUPT: {cache_key} - Invalid JSON: {e}")
        try:
            blob_client.delete_blob()
        except:
            pass
        return None
    except Exception as e:
        # Any other error - log and treat as cache miss for graceful degradation
        logging.warning(f"Cache ERROR: {cache_key} - {type(e).__name__}: {e}")
        return None


def save_cached_data(blob_container, cache_key, data, ttl_seconds=DEFAULT_TTL_SECONDS):
    """
    Save data to blob storage cache.

    Args:
        blob_container: Azure Blob ContainerClient instance
        cache_key: Cache key (e.g., 'posts', 'comments-0001')
        data: Data to cache (must be JSON serializable)
        ttl_seconds: Time-to-live in seconds (for metadata only)

    Returns:
        True if successful, False otherwise

    Raises:
        No exceptions raised - logs errors and returns False for graceful degradation
    """
    try:
        blob_name = f"{CACHE_FOLDER}/{cache_key}.json"
        blob_client = blob_container.get_blob_client(blob_name)

        # Create cache envelope with metadata
        cache_content = {
            'data': data,
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'ttl_seconds': ttl_seconds
        }

        # Upload to blob storage
        blob_client.upload_blob(
            json.dumps(cache_content),
            overwrite=True,
            content_settings=ContentSettings(content_type='application/json')
        )

        logging.info(f"Cache SAVE: {cache_key} (TTL: {ttl_seconds}s)")
        return True

    except Exception as e:
        # Log error but don't fail the function - cache save is not critical
        logging.error(f"Cache SAVE ERROR: {cache_key} - {type(e).__name__}: {e}")
        return False


def invalidate_cache(blob_container, cache_key):
    """
    Invalidate (delete) a specific cache entry.

    Args:
        blob_container: Azure Blob ContainerClient instance
        cache_key: Cache key to invalidate (e.g., 'posts', 'comments-0001')

    Returns:
        True if deleted or didn't exist, False on error

    Raises:
        No exceptions raised - logs errors and returns status
    """
    try:
        blob_name = f"{CACHE_FOLDER}/{cache_key}.json"
        blob_client = blob_container.get_blob_client(blob_name)
        blob_client.delete_blob()

        logging.info(f"Cache INVALIDATE: {cache_key}")
        return True

    except ResourceNotFoundError:
        # Cache doesn't exist - that's fine, it's invalidated
        logging.info(f"Cache INVALIDATE: {cache_key} (already deleted or never existed)")
        return True
    except Exception as e:
        # Log error but don't fail the function
        logging.warning(f"Cache INVALIDATE ERROR: {cache_key} - {type(e).__name__}: {e}")
        return False


def invalidate_multiple_caches(blob_container, cache_keys):
    """
    Invalidate multiple cache entries at once.

    Args:
        blob_container: Azure Blob ContainerClient instance
        cache_keys: List of cache keys to invalidate

    Returns:
        Dictionary with results: {cache_key: success_boolean}
    """
    results = {}
    for cache_key in cache_keys:
        results[cache_key] = invalidate_cache(blob_container, cache_key)

    successful = sum(1 for v in results.values() if v)
    logging.info(f"Cache INVALIDATE BATCH: {successful}/{len(cache_keys)} succeeded")

    return results
