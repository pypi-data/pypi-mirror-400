"""DNS caching utilities for improved resiliency to DNS outages."""

import time
import socket
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class DNSCache:
    """
    A simple in-memory DNS cache that stores resolved IP addresses.
    
    This cache is used as a fallback mechanism when DNS resolution fails,
    providing last known IPs for hosts even during DNS server outages.
    """
    
    def __init__(self, ttl_seconds: int = 86400):  # Default TTL: 24 hours
        """
        Initialize the DNS cache.
        
        Args:
            ttl_seconds: Time-to-live in seconds for cached entries (default: 24 hours)
        """
        self._cache: Dict[str, Tuple[str, float]] = {}  # hostname -> (ip, timestamp)
        self.ttl_seconds = ttl_seconds
        logger.debug(f"DNS cache initialized with {ttl_seconds}s TTL")
    
    def get(self, hostname: str) -> Optional[str]:
        """
        Get cached IP address for a hostname if available and not expired.
        
        Args:
            hostname: The hostname to lookup
            
        Returns:
            The cached IP address or None if not in cache or expired
        """
        if hostname in self._cache:
            ip, timestamp = self._cache[hostname]
            now = time.time()
            
            # Check if the entry has expired
            if now - timestamp < self.ttl_seconds:
                logger.debug(f"DNS cache hit for {hostname} -> {ip}")
                return ip
            else:
                logger.debug(f"DNS cache entry for {hostname} expired (age: {now - timestamp:.1f}s)")
                del self._cache[hostname]
        
        return None
    
    def set(self, hostname: str, ip: str):
        """
        Cache an IP address for a hostname.
        
        Args:
            hostname: The hostname to cache
            ip: The resolved IP address
        """
        self._cache[hostname] = (ip, time.time())
        logger.debug(f"DNS cache updated: {hostname} -> {ip}")
    
    def resolve(self, hostname: str) -> str:
        """
        Resolve a hostname to an IP address, using cache when possible.
        
        This method first tries a normal DNS resolution. If that fails,
        it falls back to the cached IP address if available.
        
        Args:
            hostname: The hostname to resolve
            
        Returns:
            The resolved IP address
            
        Raises:
            socket.gaierror: If hostname cannot be resolved and no cache entry exists
        """
        # First check if it's already an IP address
        if self._is_ip_address(hostname):
            return hostname
            
        # Try normal DNS resolution first
        try:
            ip = socket.gethostbyname(hostname)
            # Update the cache on successful resolution
            self.set(hostname, ip)
            return ip
        except socket.gaierror as e:
            # DNS resolution failed, try to use cached entry
            cached_ip = self.get(hostname)
            if cached_ip:
                logger.info(f"DNS resolution failed for {hostname}, using cached IP {cached_ip}")
                return cached_ip
            else:
                # No cached entry available, re-raise the exception
                logger.warning(f"DNS resolution failed for {hostname} and no cache entry available")
                raise e
    
    def _is_ip_address(self, hostname: str) -> bool:
        """
        Check if a string is already an IP address.
        
        Args:
            hostname: String to check
            
        Returns:
            True if string is an IP address, False otherwise
        """
        try:
            # Attempt to parse as IPv4 address
            parts = hostname.split('.')
            if len(parts) != 4:
                return False
                
            # Check if all parts are integers between 0 and 255
            return all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False
            
    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        logger.debug("DNS cache cleared")
        
    def __len__(self):
        """Return the number of entries in the cache."""
        return len(self._cache) 