"""
Simple cache system for BOAMP tenders

This module implements a simple file-based cache to avoid re-scraping
the same tenders multiple times.

Usage:
    from boamp.cache import TenderCache
    
    cache = TenderCache()
    
    # Check if tender is cached
    if cache.is_cached(tender_id):
        tender = cache.get(tender_id)
    else:
        tender = await scrape_tender(tender_id)
        cache.set(tender_id, tender)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from .models import Tender

logger = logging.getLogger(__name__)


class TenderCache:
    """
    Simple file-based cache for tender data.
    
    Stores tenders as JSON files in a cache directory to avoid
    re-scraping the same data repeatedly.
    
    Attributes:
        cache_dir: Directory where cache files are stored
        ttl: Time-to-live for cache entries in seconds (default: 24 hours)
    
    Example:
        ```python
        cache = TenderCache(ttl=3600)  # 1 hour TTL
        
        # Store tender
        cache.set(tender.id, tender)
        
        # Retrieve tender
        if cache.is_cached(tender.id):
            tender = cache.get(tender.id)
        
        # Clear old entries
        cache.cleanup()
        ```
    """
    
    def __init__(
        self,
        cache_dir: str = ".cache/tenders",
        ttl: int = 86400  # 24 hours default
    ):
        """
        Initialize tender cache.
        
        Args:
            cache_dir: Directory to store cache files (default: .cache/tenders)
            ttl: Time-to-live in seconds (default: 86400 = 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"TenderCache initialized: dir={cache_dir}, ttl={ttl}s")
    
    def _get_cache_path(self, tender_id: str) -> Path:
        """Get path to cache file for a tender ID"""
        # Use hash to avoid filesystem issues with special characters
        safe_id = hashlib.md5(tender_id.encode()).hexdigest()
        return self.cache_dir / f"{safe_id}.json"
    
    def is_cached(self, tender_id: str) -> bool:
        """
        Check if a tender is cached and not expired.
        
        Args:
            tender_id: The tender ID to check
        
        Returns:
            True if cached and not expired, False otherwise
        """
        cache_path = self._get_cache_path(tender_id)
        
        if not cache_path.exists():
            return False
        
        # Check if expired
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data["cached_at"])
            age = (datetime.now() - cached_time).total_seconds()
            
            if age > self.ttl:
                logger.debug(f"Cache expired for {tender_id} (age: {age:.0f}s)")
                cache_path.unlink()  # Delete expired cache
                return False
            
            return True
        
        except Exception as e:
            logger.warning(f"Error checking cache for {tender_id}: {e}")
            return False
    
    def get(self, tender_id: str) -> Optional[Tender]:
        """
        Get a tender from cache.
        
        Args:
            tender_id: The tender ID to retrieve
        
        Returns:
            Tender object if found and valid, None otherwise
        """
        if not self.is_cached(tender_id):
            return None
        
        cache_path = self._get_cache_path(tender_id)
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            tender_data = data["tender"]
            tender = Tender(**tender_data)
            
            logger.debug(f"✅ Cache hit for {tender_id}")
            return tender
        
        except Exception as e:
            logger.warning(f"Error loading cache for {tender_id}: {e}")
            return None
    
    def set(self, tender_id: str, tender: Tender):
        """
        Store a tender in cache.
        
        Args:
            tender_id: The tender ID
            tender: The tender object to cache
        """
        cache_path = self._get_cache_path(tender_id)
        
        try:
            data = {
                "tender_id": tender_id,
                "cached_at": datetime.now().isoformat(),
                "tender": tender.model_dump()
            }
            
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.debug(f"💾 Cached tender {tender_id}")
        
        except Exception as e:
            logger.warning(f"Error caching tender {tender_id}: {e}")
    
    def get_many(self, tender_ids: List[str]) -> Dict[str, Tender]:
        """
        Get multiple tenders from cache.
        
        Args:
            tender_ids: List of tender IDs to retrieve
        
        Returns:
            Dict mapping tender IDs to Tender objects (only cached ones)
        """
        results = {}
        
        for tender_id in tender_ids:
            tender = self.get(tender_id)
            if tender:
                results[tender_id] = tender
        
        logger.debug(f"Cache hit for {len(results)}/{len(tender_ids)} tenders")
        return results
    
    def set_many(self, tenders: List[Tender]):
        """
        Store multiple tenders in cache.
        
        Args:
            tenders: List of tender objects to cache
        """
        for tender in tenders:
            self.set(tender.id, tender)
        
        logger.debug(f"💾 Cached {len(tenders)} tenders")
    
    def delete(self, tender_id: str):
        """
        Delete a tender from cache.
        
        Args:
            tender_id: The tender ID to delete
        """
        cache_path = self._get_cache_path(tender_id)
        
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"🗑️  Deleted cache for {tender_id}")
    
    def cleanup(self, older_than: Optional[int] = None):
        """
        Remove expired cache entries.
        
        Args:
            older_than: Remove entries older than this many seconds
                       (default: use the cache TTL)
        """
        if older_than is None:
            older_than = self.ttl
        
        cutoff = datetime.now() - timedelta(seconds=older_than)
        deleted = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                cached_time = datetime.fromisoformat(data["cached_at"])
                
                if cached_time < cutoff:
                    cache_file.unlink()
                    deleted += 1
            
            except Exception as e:
                logger.warning(f"Error cleaning up {cache_file}: {e}")
        
        if deleted > 0:
            logger.info(f"🗑️  Cleaned up {deleted} expired cache entries")
    
    def clear(self):
        """Clear all cache entries"""
        deleted = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            deleted += 1
        
        logger.info(f"🗑️  Cleared {deleted} cache entries")
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats (count, size, oldest, newest)
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        
        if not cache_files:
            return {
                "count": 0,
                "size_bytes": 0,
                "oldest": None,
                "newest": None,
            }
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        times = []
        for cache_file in cache_files:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                times.append(datetime.fromisoformat(data["cached_at"]))
            except Exception:
                pass
        
        return {
            "count": len(cache_files),
            "size_bytes": total_size,
            "size_mb": total_size / (1024 * 1024),
            "oldest": min(times).isoformat() if times else None,
            "newest": max(times).isoformat() if times else None,
        }


# Global cache instance (can be imported and reused)
default_cache = TenderCache()

