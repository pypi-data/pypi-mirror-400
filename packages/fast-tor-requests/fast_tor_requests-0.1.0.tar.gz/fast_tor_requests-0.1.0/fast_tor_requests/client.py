import requests
import uuid


class TorSession(requests.Session):
    """
    Drop-in replacement for requests.Session
    using Tor + IsolateSOCKSAuth for fast IP rotation.
    """

    def __init__(
        self,
        tor_host="127.0.0.1",
        tor_port=9050,
        timeout=25,
        user_agent=None
    ):
        super().__init__()

        self.tor_host = tor_host
        self.tor_port = tor_port
        self.timeout = timeout

        self.headers.update({
            "User-Agent": user_agent or
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def _tor_proxies(self):
        auth = uuid.uuid4().hex
        proxy = f"socks5h://{auth}:x@{self.tor_host}:{self.tor_port}"
        return {
            "http": proxy,
            "https": proxy,
        }

    def request(self, method, url, **kwargs):
        # Default timeout
        kwargs.setdefault("timeout", self.timeout)

        # Use Tor proxies unless user overrides
        if "proxies" not in kwargs:
            kwargs["proxies"] = self._tor_proxies()

        return super().request(method, url, **kwargs)
