# -*- coding:utf-8 -*-
"""
@Author   : Enhanced by AI
@Purpose  : WebSocket listener for DrissionPage
"""
from queue import Queue, Empty
from re import search
from .listener import Listener


class WebSocketListener(Listener):
    """Listen to WebSocket frames from browser tabs"""
    
    def __init__(self, owner, targets=True, is_regex=False):
        super().__init__(owner)
        self._targets = targets
        self._is_regex = is_regex
        self._active_ws = set()
        self._frames = Queue()
    
    def _set_callback(self):
        """Set WebSocket-specific callbacks"""
        super()._set_callback()
        self._driver.set_callback("Network.webSocketCreated", self._on_ws_created)
        self._driver.set_callback("Network.webSocketFrameReceived", self._on_ws_frame_received)
        self._driver.set_callback("Network.webSocketFrameSent", self._on_ws_frame_sent)
        self._driver.set_callback("Network.webSocketClosed", self._on_ws_closed)
    
    def _on_ws_created(self, **kwargs):
        """Handle WebSocket creation"""
        url = kwargs.get("url")
        if url and self._match_url(url):
            self._active_ws.add(kwargs["requestId"])
    
    def _on_ws_frame_received(self, **kwargs):
        """Handle received WebSocket frame"""
        if kwargs["requestId"] in self._active_ws:
            kwargs["_direction"] = "received"
            self._frames.put(kwargs)
    
    def _on_ws_frame_sent(self, **kwargs):
        """Handle sent WebSocket frame"""
        if kwargs["requestId"] in self._active_ws:
            kwargs["_direction"] = "sent"
            self._frames.put(kwargs)
    
    def _on_ws_closed(self, **kwargs):
        """Handle WebSocket closure"""
        self._active_ws.discard(kwargs["requestId"])
    
    def _match_url(self, url):
        """Check if URL matches target patterns"""
        if self._targets is True:
            return True
        if isinstance(self._targets, str):
            targets = {self._targets}
        else:
            targets = self._targets
        
        if self._is_regex:
            return any(search(t, url) for t in targets)
        return any(t in url for t in targets)
    
    def get_frame(self, timeout=None):
        """Get next frame (blocking)"""
        return self._frames.get(timeout=timeout)
    
    def get_frame_nowait(self):
        """Get next frame (non-blocking)"""
        return self._frames.get_nowait()
    
    def clear_frames(self):
        """Clear all queued frames"""
        while not self._frames.empty():
            try:
                self._frames.get_nowait()
            except Empty:
                break
