# -*- coding:utf-8 -*-
from typing import Optional, Dict, Any


class ProxyAuth:
    _owner: Any
    _enabled: bool
    _username: Optional[str]
    _password: Optional[str]
    
    def __init__(self, owner: Any) -> None: ...
    
    def enable(self, proxy_url: str) -> bool: ...
    
    def disable(self) -> None: ...
    
    def _parse_proxy(self, proxy_url: str) -> Optional[Dict[str, str]]: ...
    
    def _on_auth_required(self, **kwargs: Any) -> None: ...
    
    def _on_request_paused(self, **kwargs: Any) -> None: ...
