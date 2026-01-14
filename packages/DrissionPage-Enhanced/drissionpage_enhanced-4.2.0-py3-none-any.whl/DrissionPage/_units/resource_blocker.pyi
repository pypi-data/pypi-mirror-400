# -*- coding:utf-8 -*-
from typing import Optional, List, Any


class ResourceBlocker:
    _owner: Any
    _enabled: bool
    _block_images: bool
    _block_css: bool
    _block_fonts: bool
    _block_media: bool
    _custom_patterns: List[str]
    
    def __init__(self, owner: Any) -> None: ...
    
    def enable(self, 
              images: bool = False, 
              css: bool = False, 
              fonts: bool = False, 
              media: bool = False, 
              patterns: Optional[List[str]] = None) -> None: ...
    
    def disable(self) -> None: ...
    
    def _should_block(self, resource_type: str, url: str) -> bool: ...
    
    def _on_request(self, **kwargs: Any) -> None: ...
