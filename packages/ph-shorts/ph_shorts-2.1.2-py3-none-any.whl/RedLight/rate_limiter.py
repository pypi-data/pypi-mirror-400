import time
import threading
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    requests_per_second: float = 2.0
    requests_per_minute: int = 60
    burst_limit: int = 5
    backoff_multiplier: float = 2.0
    max_backoff: float = 60.0


class RateLimiter:
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._site_configs: Dict[str, RateLimitConfig] = {}
        self._last_request: Dict[str, float] = defaultdict(float)
        self._request_counts: Dict[str, list] = defaultdict(list)
        self._backoff_until: Dict[str, float] = defaultdict(float)
        self._current_backoff: Dict[str, float] = defaultdict(lambda: 1.0)
        self._lock = threading.Lock()
        self._initialized = True
        
        self._default_configs = {
            "pornhub": RateLimitConfig(requests_per_second=1.0, requests_per_minute=30),
            "xvideos": RateLimitConfig(requests_per_second=2.0, requests_per_minute=60),
            "xhamster": RateLimitConfig(requests_per_second=1.5, requests_per_minute=45),
            "eporner": RateLimitConfig(requests_per_second=2.0, requests_per_minute=60),
            "spankbang": RateLimitConfig(requests_per_second=1.0, requests_per_minute=30),
            "xnxx": RateLimitConfig(requests_per_second=2.0, requests_per_minute=60),
            "youporn": RateLimitConfig(requests_per_second=1.5, requests_per_minute=45),
        }
    
    def SetSiteConfig(self, site: str, config: RateLimitConfig):
        self._site_configs[site.lower()] = config
    
    def GetConfig(self, site: str) -> RateLimitConfig:
        site = site.lower()
        if site in self._site_configs:
            return self._site_configs[site]
        if site in self._default_configs:
            return self._default_configs[site]
        return RateLimitConfig()
    
    def Wait(self, site: str) -> float:
        site = site.lower()
        config = self.GetConfig(site)
        
        with self._lock:
            now = time.time()
            
            if self._backoff_until[site] > now:
                wait_time = self._backoff_until[site] - now
                time.sleep(wait_time)
                return wait_time
            
            min_interval = 1.0 / config.requests_per_second
            time_since_last = now - self._last_request[site]
            
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                time.sleep(wait_time)
                self._last_request[site] = time.time()
                return wait_time
            
            self._cleanup_old_requests(site)
            
            if len(self._request_counts[site]) >= config.requests_per_minute:
                oldest = self._request_counts[site][0]
                wait_time = 60.0 - (now - oldest)
                if wait_time > 0:
                    time.sleep(wait_time)
            
            self._last_request[site] = time.time()
            self._request_counts[site].append(time.time())
            self._current_backoff[site] = 1.0
            
            return 0.0
    
    def _cleanup_old_requests(self, site: str):
        now = time.time()
        cutoff = now - 60.0
        self._request_counts[site] = [t for t in self._request_counts[site] if t > cutoff]
    
    def ReportError(self, site: str, status_code: int = 0):
        site = site.lower()
        config = self.GetConfig(site)
        
        with self._lock:
            if status_code == 429 or status_code == 503:
                backoff = self._current_backoff[site] * config.backoff_multiplier
                backoff = min(backoff, config.max_backoff)
                self._current_backoff[site] = backoff
                self._backoff_until[site] = time.time() + backoff
    
    def ReportSuccess(self, site: str):
        site = site.lower()
        with self._lock:
            self._current_backoff[site] = 1.0
    
    def GetStatus(self) -> Dict[str, dict]:
        now = time.time()
        status = {}
        
        for site in set(list(self._last_request.keys()) + list(self._default_configs.keys())):
            config = self.GetConfig(site)
            self._cleanup_old_requests(site)
            
            status[site] = {
                "requests_last_minute": len(self._request_counts[site]),
                "limit_per_minute": config.requests_per_minute,
                "in_backoff": self._backoff_until[site] > now,
                "backoff_remaining": max(0, self._backoff_until[site] - now),
                "current_backoff_multiplier": self._current_backoff[site]
            }
        
        return status
    
    def Reset(self, site: Optional[str] = None):
        with self._lock:
            if site:
                site = site.lower()
                self._last_request[site] = 0
                self._request_counts[site] = []
                self._backoff_until[site] = 0
                self._current_backoff[site] = 1.0
            else:
                self._last_request.clear()
                self._request_counts.clear()
                self._backoff_until.clear()
                self._current_backoff.clear()


_rate_limiter: Optional[RateLimiter] = None


def GetRateLimiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def RateLimitedRequest(site: str):
    return GetRateLimiter().Wait(site)
