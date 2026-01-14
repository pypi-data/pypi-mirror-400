"""
Proxy-Aware Fetcher

Detects proxy requirements and routes fetches through proxy or direct with clear errors.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import os


@dataclass
class FetchResult:
    success: bool
    status: int
    content: Optional[str]
    error: Optional[str]
    route: str


class ProxyAwareFetcher:
    def __init__(self, proxy_url: Optional[str] = None, no_proxy: Optional[str] = None):
        self.proxy_url = proxy_url or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        self.no_proxy = no_proxy or os.getenv("NO_PROXY", "")

    def detect_proxy_requirements(self, url: str) -> bool:
        return bool(self.proxy_url) and not any(host for host in self.no_proxy.split(",") if host and host in url)

    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> FetchResult:
        use_proxy = self.detect_proxy_requirements(url)
        try:
            import requests

            proxies = {"http": self.proxy_url, "https": self.proxy_url} if use_proxy else None
            resp = requests.get(url, headers=headers or {}, proxies=proxies, timeout=20)
            return FetchResult(True, resp.status_code, resp.text, None, "proxy" if use_proxy else "direct")
        except Exception as e:
            return FetchResult(False, 0, None, str(e), "proxy" if use_proxy else "direct")


def load_proxy_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return config
