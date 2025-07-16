"""
Proxy Manager for AI API requests
"""
import os
import logging
from typing import Optional, Dict
from contextlib import contextmanager


class ProxyManager:
    """代理管理器，用于在AI请求前后设置和清理代理"""
    
    def __init__(self, enabled: bool = False, http_proxy: str = None, https_proxy: str = None):
        self.enabled = enabled
        self.http_proxy = http_proxy
        self.https_proxy = https_proxy
        self.logger = logging.getLogger(__name__)
        self._original_env = {}
    
    @contextmanager
    def proxy_context(self):
        """代理上下文管理器，自动设置和清理代理"""
        if not self.enabled:
            yield
            return
        
        try:
            self._set_proxy()
            self.logger.info("Proxy enabled for AI request")
            yield
        finally:
            self._clear_proxy()
            self.logger.info("Proxy cleared after AI request")
    
    def _set_proxy(self):
        """设置代理环境变量"""
        if not self.enabled:
            return
        
        # 保存原始环境变量
        self._original_env = {
            'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
            'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
            'http_proxy': os.environ.get('http_proxy'),
            'https_proxy': os.environ.get('https_proxy')
        }
        
        # 设置代理
        if self.http_proxy:
            os.environ['HTTP_PROXY'] = self.http_proxy
            os.environ['http_proxy'] = self.http_proxy
        
        if self.https_proxy:
            os.environ['HTTPS_PROXY'] = self.https_proxy
            os.environ['https_proxy'] = self.https_proxy
        
        self.logger.debug(f"Proxy set - HTTP: {self.http_proxy}, HTTPS: {self.https_proxy}")
    
    def _clear_proxy(self):
        """清理代理环境变量，恢复原始状态"""
        if not self.enabled:
            return
        
        # 恢复原始环境变量
        for key, value in self._original_env.items():
            if value is None:
                # 如果原来没有这个环境变量，则删除它
                os.environ.pop(key, None)
            else:
                # 如果原来有这个环境变量，则恢复它
                os.environ[key] = value
        
        self.logger.debug("Proxy environment variables restored")
    
    @classmethod
    def from_config(cls, config: Dict) -> 'ProxyManager':
        """从配置创建代理管理器"""
        return cls(
            enabled=config.get('proxy_enabled', False),
            http_proxy=config.get('proxy_http'),
            https_proxy=config.get('proxy_https')
        )