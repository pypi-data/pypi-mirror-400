# -*- coding:utf-8 -*-
"""
@Author   : Enhanced by AI
@Purpose  : Proxy authentication handler for DrissionPage
"""
from base64 import b64encode
from re import match


class ProxyAuth:
    """Handle proxy authentication via CDP"""
    
    def __init__(self, owner):
        self._owner = owner
        self._enabled = False
        self._username = None
        self._password = None
        
    def enable(self, proxy_url):
        """
        Enable proxy authentication from proxy URL
        Format: username:password@host:port or http://username:password@host:port
        """
        parsed = self._parse_proxy(proxy_url)
        if not parsed:
            return False
            
        self._username = parsed['username']
        self._password = parsed['password']
        
        if not self._enabled:
            self._owner._run_cdp('Fetch.enable', handleAuthRequests=True)
            self._owner.driver.set_callback('Fetch.requestPaused', self._on_request_paused, immediate=True)
            self._owner.driver.set_callback('Fetch.authRequired', self._on_auth_required, immediate=True)
            self._enabled = True
        return True
    
    def disable(self):
        """Disable proxy authentication"""
        if self._enabled:
            self._owner._run_cdp('Fetch.disable')
            self._owner.driver.set_callback('Fetch.requestPaused', None)
            self._owner.driver.set_callback('Fetch.authRequired', None)
            self._enabled = False
            self._username = None
            self._password = None
    
    def _parse_proxy(self, proxy_url):
        """Parse proxy URL to extract credentials"""
        # Match: username:password@host:port or http://username:password@host:port
        pattern = r'(?:https?://)?([^:]+):([^@]+)@(.+)'
        m = match(pattern, proxy_url)
        if m:
            return {
                'username': m.group(1),
                'password': m.group(2),
                'host': m.group(3)
            }
        return None
    
    def _on_auth_required(self, **kwargs):
        """Handle authentication challenge"""
        if self._username and self._password:
            self._owner.driver.run('Fetch.continueWithAuth',
                                  requestId=kwargs['requestId'],
                                  authChallengeResponse={
                                      'response': 'ProvideCredentials',
                                      'username': self._username,
                                      'password': self._password
                                  }, _timeout=0)
    
    def _on_request_paused(self, **kwargs):
        """Continue paused requests"""
        self._owner.driver.run('Fetch.continueRequest', requestId=kwargs['requestId'], _timeout=0)
