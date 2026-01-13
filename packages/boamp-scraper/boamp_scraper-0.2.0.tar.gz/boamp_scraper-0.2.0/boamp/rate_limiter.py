"""
Rate Limiter for BOAMP scraping

This module implements a simple rate limiter to be respectful to BOAMP servers
and avoid overwhelming them with requests.

Usage:
    from boamp.rate_limiter import RateLimiter
    
    limiter = RateLimiter(requests_per_minute=10)
    
    async with limiter:
        # Your scraping code here
        await scrape_boamp()
"""

import asyncio
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter for API/scraping requests.
    
    Ensures we don't exceed a certain number of requests per minute
    to be respectful to the server.
    
    Attributes:
        requests_per_minute: Maximum number of requests allowed per minute
        min_delay: Minimum delay between requests in seconds
    
    Example:
        ```python
        limiter = RateLimiter(requests_per_minute=10)
        
        # Using as context manager
        async with limiter:
            await scrape_page()
        
        # Or explicit wait
        await limiter.wait()
        ```
    """
    
    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute (default: 10)
                This means one request every 6 seconds minimum.
        """
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / requests_per_minute  # Delay in seconds
        self.last_request_time: Optional[float] = None
        self._lock = asyncio.Lock()
        
        logger.debug(
            f"RateLimiter initialized: {requests_per_minute} req/min "
            f"(min delay: {self.min_delay:.2f}s)"
        )
    
    async def wait(self):
        """
        Wait if necessary to respect rate limit.
        
        This method calculates how long we need to wait since the last request
        and sleeps for that duration to maintain the rate limit.
        """
        async with self._lock:
            if self.last_request_time is not None:
                elapsed = time.time() - self.last_request_time
                remaining = self.min_delay - elapsed
                
                if remaining > 0:
                    logger.debug(f"⏳ Rate limiting: waiting {remaining:.2f}s")
                    await asyncio.sleep(remaining)
            
            self.last_request_time = time.time()
            logger.debug("✅ Rate limit check passed")
    
    async def __aenter__(self):
        """Context manager entry: wait for rate limit"""
        await self.wait()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        return False
    
    def reset(self):
        """Reset the rate limiter (useful for testing)"""
        self.last_request_time = None
        logger.debug("Rate limiter reset")


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts speed based on errors.
    
    If we encounter too many errors (e.g., timeouts, 429s), 
    this limiter will slow down automatically.
    
    Example:
        ```python
        limiter = AdaptiveRateLimiter(
            requests_per_minute=10,
            slowdown_factor=2.0
        )
        
        try:
            async with limiter:
                await scrape_page()
        except Exception:
            limiter.record_error()
            # Limiter will automatically slow down
        ```
    """
    
    def __init__(
        self,
        requests_per_minute: int = 10,
        slowdown_factor: float = 2.0,
        recovery_threshold: int = 5
    ):
        """
        Initialize adaptive rate limiter.
        
        Args:
            requests_per_minute: Base requests per minute
            slowdown_factor: Factor to slow down by when errors occur (default: 2.0)
            recovery_threshold: Number of successful requests before speeding up
        """
        super().__init__(requests_per_minute)
        self.base_requests_per_minute = requests_per_minute
        self.slowdown_factor = slowdown_factor
        self.recovery_threshold = recovery_threshold
        self.error_count = 0
        self.success_count = 0
        self.current_level = 0  # 0 = normal, 1 = slow, 2 = slower, etc.
        
        logger.debug(
            f"AdaptiveRateLimiter initialized: base={requests_per_minute} req/min, "
            f"slowdown={slowdown_factor}x"
        )
    
    def record_error(self):
        """Record an error and potentially slow down"""
        self.error_count += 1
        self.success_count = 0
        
        # Slow down after 2 consecutive errors
        if self.error_count >= 2:
            self._slow_down()
    
    def record_success(self):
        """Record a successful request and potentially speed up"""
        self.success_count += 1
        self.error_count = 0
        
        # Speed up after recovery_threshold successes
        if self.success_count >= self.recovery_threshold:
            self._speed_up()
    
    def _slow_down(self):
        """Slow down the rate limiter"""
        self.current_level += 1
        new_rate = self.base_requests_per_minute / (
            self.slowdown_factor ** self.current_level
        )
        self.requests_per_minute = int(max(1, new_rate))
        self.min_delay = 60.0 / self.requests_per_minute
        
        logger.warning(
            f"🐌 Rate limiter slowing down to level {self.current_level}: "
            f"{self.requests_per_minute} req/min (delay: {self.min_delay:.2f}s)"
        )
        
        self.error_count = 0
    
    def _speed_up(self):
        """Speed up the rate limiter (recovery)"""
        if self.current_level > 0:
            self.current_level -= 1
            new_rate = self.base_requests_per_minute / (
                self.slowdown_factor ** self.current_level
            )
            self.requests_per_minute = int(new_rate)
            self.min_delay = 60.0 / self.requests_per_minute
            
            logger.info(
                f"🚀 Rate limiter speeding up to level {self.current_level}: "
                f"{self.requests_per_minute} req/min (delay: {self.min_delay:.2f}s)"
            )
        
        self.success_count = 0


# Global rate limiter instance (can be imported and reused)
default_limiter = RateLimiter(requests_per_minute=10)

