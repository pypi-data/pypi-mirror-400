# -*- coding:utf-8 -*-
"""
@Author   : Enhanced by AI
@Purpose  : Advanced resource blocking for DrissionPage
"""


class ResourceBlocker:
    """Advanced resource blocking using CDP Fetch domain"""
    
    def __init__(self, owner):
        self._owner = owner
        self._enabled = False
        self._block_images = False
        self._block_css = False
        self._block_fonts = False
        self._block_media = False
        self._custom_patterns = []
        
    def enable(self, images=False, css=False, fonts=False, media=False, patterns=None):
        """
        Enable resource blocking
        :param images: Block images
        :param css: Block CSS
        :param fonts: Block fonts
        :param media: Block media (video/audio)
        :param patterns: List of URL patterns to block
        """
        self._block_images = images
        self._block_css = css
        self._block_fonts = fonts
        self._block_media = media
        self._custom_patterns = patterns or []
        
        if not self._enabled:
            # Use Fetch domain for interception
            self._owner._run_cdp('Fetch.enable', 
                               patterns=[{'urlPattern': '*', 'resourceType': 'Document'},
                                       {'urlPattern': '*', 'resourceType': 'Stylesheet'},
                                       {'urlPattern': '*', 'resourceType': 'Image'},
                                       {'urlPattern': '*', 'resourceType': 'Media'},
                                       {'urlPattern': '*', 'resourceType': 'Font'},
                                       {'urlPattern': '*', 'resourceType': 'Script'},
                                       {'urlPattern': '*', 'resourceType': 'XHR'},
                                       {'urlPattern': '*', 'resourceType': 'Fetch'}])
            self._owner.driver.set_callback('Fetch.requestPaused', self._on_request, immediate=True)
            self._enabled = True
    
    def disable(self):
        """Disable resource blocking"""
        if self._enabled:
            self._owner._run_cdp('Fetch.disable')
            self._owner.driver.set_callback('Fetch.requestPaused', None)
            self._enabled = False
            self._block_images = False
            self._block_css = False
            self._block_fonts = False
            self._block_media = False
            self._custom_patterns = []
    
    def _should_block(self, resource_type, url):
        """Determine if resource should be blocked"""
        if self._block_images and resource_type == 'Image':
            return True
        if self._block_css and resource_type == 'Stylesheet':
            return True
        if self._block_fonts and resource_type == 'Font':
            return True
        if self._block_media and resource_type == 'Media':
            return True
        
        # Check custom patterns
        for pattern in self._custom_patterns:
            if pattern in url:
                return True
        
        return False
    
    def _on_request(self, **kwargs):
        """Handle intercepted requests"""
        resource_type = kwargs.get('resourceType', '')
        url = kwargs.get('request', {}).get('url', '')
        request_id = kwargs['requestId']
        
        if self._should_block(resource_type, url):
            # Fail the request to block it
            self._owner.driver.run('Fetch.failRequest', 
                                  requestId=request_id,
                                  errorReason='BlockedByClient', _timeout=0)
        else:
            # Continue the request
            self._owner.driver.run('Fetch.continueRequest', requestId=request_id, _timeout=0)
