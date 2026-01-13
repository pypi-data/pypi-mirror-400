import random
import threading
import time
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class ProxyConfig:
    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    is_alive: bool = True
    last_check: float = 0
    fail_count: int = 0
    
    def to_url(self) -> str:
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        return f"{self.proxy_type.value}://{auth}{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, str]:
        url = self.to_url()
        return {"http": url, "https": url}


class ProxyManager:
    
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
        
        self._proxies: List[ProxyConfig] = []
        self._current_index = 0
        self._enabled = False
        self._auto_rotate = True
        self._rotate_on_fail = True
        self._max_fails = 3
        self._check_interval = 300
        self._last_check = 0
        self._lock = threading.Lock()
        self._initialized = True
    
    def AddProxy(
        self,
        host: str,
        port: int,
        proxy_type: str = "http",
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> bool:
        try:
            ptype = ProxyType(proxy_type.lower())
            proxy = ProxyConfig(
                host=host,
                port=port,
                proxy_type=ptype,
                username=username,
                password=password
            )
            self._proxies.append(proxy)
            return True
        except Exception:
            return False
    
    def AddProxyFromUrl(self, url: str) -> bool:
        try:
            if "://" in url:
                proto, rest = url.split("://", 1)
            else:
                proto = "http"
                rest = url
            
            auth = None
            if "@" in rest:
                auth, hostport = rest.rsplit("@", 1)
            else:
                hostport = rest
            
            if ":" in hostport:
                host, port = hostport.rsplit(":", 1)
                port = int(port)
            else:
                host = hostport
                port = 8080
            
            username, password = None, None
            if auth and ":" in auth:
                username, password = auth.split(":", 1)
            
            return self.AddProxy(host, port, proto, username, password)
        except Exception:
            return False
    
    def RemoveProxy(self, index: int) -> bool:
        with self._lock:
            if 0 <= index < len(self._proxies):
                self._proxies.pop(index)
                if self._current_index >= len(self._proxies):
                    self._current_index = 0
                return True
        return False
    
    def ClearProxies(self):
        with self._lock:
            self._proxies.clear()
            self._current_index = 0
    
    def GetCurrentProxy(self) -> Optional[Dict[str, str]]:
        if not self._enabled or not self._proxies:
            return None
        
        with self._lock:
            proxy = self._proxies[self._current_index]
            if not proxy.is_alive and self._auto_rotate:
                self._rotate_to_alive()
                proxy = self._proxies[self._current_index]
            return proxy.to_dict()
    
    def Rotate(self):
        with self._lock:
            if self._proxies:
                self._current_index = (self._current_index + 1) % len(self._proxies)
    
    def _rotate_to_alive(self):
        start = self._current_index
        for _ in range(len(self._proxies)):
            self._current_index = (self._current_index + 1) % len(self._proxies)
            if self._proxies[self._current_index].is_alive:
                break
            if self._current_index == start:
                break
    
    def ReportFailure(self):
        if not self._proxies:
            return
        
        with self._lock:
            proxy = self._proxies[self._current_index]
            proxy.fail_count += 1
            
            if proxy.fail_count >= self._max_fails:
                proxy.is_alive = False
            
            if self._rotate_on_fail:
                self._rotate_to_alive()
    
    def ReportSuccess(self):
        if not self._proxies:
            return
        
        with self._lock:
            proxy = self._proxies[self._current_index]
            proxy.fail_count = 0
            proxy.is_alive = True
    
    def CheckProxy(self, proxy: ProxyConfig, timeout: int = 10) -> bool:
        try:
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy.to_dict(),
                timeout=timeout
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def CheckAllProxies(self):
        for proxy in self._proxies:
            proxy.is_alive = self.CheckProxy(proxy)
            proxy.last_check = time.time()
    
    def Enable(self):
        self._enabled = True
    
    def Disable(self):
        self._enabled = False
    
    def IsEnabled(self) -> bool:
        return self._enabled
    
    def SetAutoRotate(self, enabled: bool):
        self._auto_rotate = enabled
    
    def SetRotateOnFail(self, enabled: bool):
        self._rotate_on_fail = enabled
    
    def SetMaxFails(self, count: int):
        self._max_fails = max(1, count)
    
    def GetProxyList(self) -> List[Dict[str, Any]]:
        return [
            {
                "index": i,
                "url": p.to_url(),
                "type": p.proxy_type.value,
                "is_alive": p.is_alive,
                "fail_count": p.fail_count,
                "is_current": i == self._current_index
            }
            for i, p in enumerate(self._proxies)
        ]
    
    def GetStatus(self) -> Dict[str, Any]:
        alive_count = sum(1 for p in self._proxies if p.is_alive)
        return {
            "enabled": self._enabled,
            "total": len(self._proxies),
            "alive": alive_count,
            "current_index": self._current_index,
            "auto_rotate": self._auto_rotate,
            "rotate_on_fail": self._rotate_on_fail
        }
    
    def LoadFromList(self, proxy_list: List[str]):
        for proxy_url in proxy_list:
            self.AddProxyFromUrl(proxy_url.strip())
    
    def GetRandomProxy(self) -> Optional[Dict[str, str]]:
        if not self._enabled or not self._proxies:
            return None
        
        alive_proxies = [p for p in self._proxies if p.is_alive]
        if not alive_proxies:
            return None
        
        return random.choice(alive_proxies).to_dict()


_proxy_manager: Optional[ProxyManager] = None


def GetProxyManager() -> ProxyManager:
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager
