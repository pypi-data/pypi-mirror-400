import logging
from math import log
from os import makedirs, mkdir
import os
from typing import Optional, TypedDict, NotRequired

# __all__ = [
#     "ProxiesManager",
#     "NoProxiesException",
#     "Proxy",
# ]

logger = logging.getLogger(__name__)

class NoProxiesException(Exception):
    pass


class Proxy:
    
    def __init__(self,
                 host: str,
                 port: int,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def get_proxy_url(self) -> str:

        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"http://{self.host}:{self.port}"
        
    def __str__(self):
        return self.get_proxy_url()

 


class ProxiesManager:
    def __init__(self, proxies: list[Proxy]):
        self.proxies = proxies
        self._current_index = 0


    def get_next_proxy(self) -> Proxy:
        if not self.proxies:
            raise NoProxiesException("No proxies available in the ProxiesManager.")

        proxy = self.proxies[self._current_index]
        self._current_index = (self._current_index + 1) % len(self.proxies)
        
        return proxy

    def has_proxies(self) -> bool:
        return len(self.proxies) > 0

    def reset(self):
        self._current_index = 0
        self._current_proxy = None

    def get_current_proxy(self) -> Proxy | None:
        if not self.proxies:
            return None

        return self.proxies[self._current_index]


class ProxiesLoader:

    def strings_to_proxies(self, proxy_strings: list[str]) -> list[Proxy]:
        proxies: list[Proxy] = []

        for line in proxy_strings:
            line = line.strip()
            if not line:
                continue

            proxy = self._from_string_line_to_proxy(line)
            if not proxy:
                raise ValueError(f"Invalid proxy format in line: '{line}'")

            proxies.append(proxy)

        return proxies

    def _from_string_line_to_proxy(self, line: str) -> Proxy | None:
        proxy: Proxy | None = None

        if "@" in line:
            # Format: username:password@host:port
            credentials, address = line.split("@")
            username, password = credentials.split(":")
            host, port = address.split(":")
            proxy = Proxy(
                host=host,
                port=int(port),
                username=username,
                password=password,
            )
        else:
            # Format: host:port
            line_values = line.split(":")

            if len(line_values) == 4:
                host, port, username, password = line_values
                proxy = Proxy(
                    host=host,
                    port=int(port),
                    username=username,
                    password=password,
                )

            elif len(line_values) == 2:
                host, port = line_values
                proxy = Proxy(host=host, port=int(port))

        return proxy

    def from_txt(self, path: str) -> list[Proxy]:

        proxies = []

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file at path '{path}' does not exist.")
   
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                print(line)
                line = line.strip()
                if not line:
                    continue
                

                proxy = self._from_string_line_to_proxy(line)
                if not proxy:
                    raise ValueError(f"Invalid proxy format in line: '{line}'")
                
                proxies.append(proxy)

        return proxies
