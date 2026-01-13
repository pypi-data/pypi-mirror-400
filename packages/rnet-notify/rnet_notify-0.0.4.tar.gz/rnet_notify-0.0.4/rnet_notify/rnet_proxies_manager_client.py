# This is a sample Python script.

import logging

import time
from tracemalloc import start
from typing import Optional, Unpack, TYPE_CHECKING

from rnet import Emulation, EmulationOS, EmulationOption, Method, Proxy as ProxyRNet

if TYPE_CHECKING:
    from rnet import ClientConfig, Request

from rnet.blocking import Client, Response
from .proxies_manager import ProxiesManager, Proxy

class RequestErrorException(Exception):
    pass


logger = logging.getLogger(__name__)


class RNetWrapperClient:

    def __init__(self, **kwargs: Unpack["ClientConfig"]):
        self.client_configs = kwargs
        self.client = None
        # self.client = self._create_client(**kwargs)
        self.emulation = kwargs.get("emulation", None)

    def _create_client(self, **kwargs) -> Client:
        client = Client(**kwargs)
        logger.debug(f"Created new client with configs: {kwargs}")
        return client

    def get_client(self) -> Client:
        return self.client
    
    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:


            if not self.client:
                self.client = self._create_client(**self.client_configs)

            headers = kwargs.get("headers", {})

            start = time.time()
            res = self.client.request(method=method, url=url, **kwargs)
            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()

            self._create_log(
                method=method,
                request_url=res.url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=None,
                emulation=self.emulation,
                headers=headers
            )

            

            return res
         

        except Exception as e:

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=None,
                emulation=self.emulation,
                headers=headers
            )

            raise RequestErrorException(e)
        
    def _create_log(self,
                    method: Method,
                    request_url: str,
                    status_code: int,
                    elapsed: float,
                    proxy: Optional[Proxy] = None,
                    emulation: Optional[str] = None,
                    headers: Optional[dict] = None
                    ):
        
        log_parts = [
            f"--- Request Log ---",
            f"Method: {method}",
            f"Proxy: {proxy if proxy else '-'}",
            f"URL: {request_url if request_url else '-'}",
            f"Response Status Code: {status_code if status_code else '-'}",
            f"Emulation: {emulation if emulation else '-'}",
            f"Headers: {headers if headers else '-'}",
            f"Time Taken: {elapsed:.2f} seconds"
        ]

        logger.info("\n".join(log_parts))
        

class RNetProxiesManagerClient(RNetWrapperClient):

    def __init__(self,
                 proxies_manager: ProxiesManager,
                 requests_limit_same_proxy: int = -1,
                 status_codes_to_change_proxy: list[int] = None,
                 **kwargs: Unpack["ClientConfig"]):
        
        super().__init__(**kwargs)
        self.proxies_manager = proxies_manager
        self.requests_limit_same_proxy = requests_limit_same_proxy
        self.status_codes_to_change_proxy = status_codes_to_change_proxy
        self.client_configs = kwargs
        self.client = None
        self.requests_made_with_current_proxy = 0


    def get_client(self) -> Client:
        # Logic to select a proxy from the proxies_manager would go here
        # For now, we just create a client with the stored kwargs

        client = self._create_client(**self.client_configs)
        return client
    
    def _is_proxy_change_needed(self, status_code: int, requests_made_with_current_proxy: int) -> bool:

        if self.status_codes_to_change_proxy and status_code in self.status_codes_to_change_proxy:
            return True
        
        if requests_made_with_current_proxy >= self.requests_limit_same_proxy:
            return True
        
        return False

    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:

            headers = kwargs.get("headers", {})

            if not self.client:
                self.client = self._create_client(**self.client_configs)


            start = time.time()

            current_proxy: Proxy = self.proxies_manager.get_current_proxy()
            logger.debug(f"Using proxy: {current_proxy}")
       
            if current_proxy:
                self.requests_made_with_current_proxy += 1
                res = self.client.request(method=method,
                                          url=url,
                                          proxy=ProxyRNet.all(current_proxy.get_proxy_url()),
                                          **kwargs)

            else:
                res = self.client.request(method=method, url=url, **kwargs)

            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()

            change_proxy = self._is_proxy_change_needed(
                status_code=status_code,
                requests_made_with_current_proxy=self.requests_made_with_current_proxy
            )

            if change_proxy:
                logger.debug(f"Changing proxy due to status code {status_code} "
                             f"or request limit reached ({self.requests_made_with_current_proxy}).")
                
                self.client = self._create_client(**self.client_configs)
                self.proxies_manager.get_next_proxy()
                self.requests_made_with_current_proxy = 0


            self._create_log(
                method=method,
                request_url=url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=self.emulation,
                headers=headers
            )

            return res
         

        except Exception as e:

            self.client = self._create_client(**self.client_configs)
            self.proxies_manager.get_next_proxy()
            self.requests_made_with_current_proxy = 0

            logger.error(f"Request error occurred: {e}. Changed proxy and retrying next request.")

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=self.emulation,
                headers=headers
            )
            raise RequestErrorException(e)
        
    


class RNetMultiplesEmulatorsClient(RNetWrapperClient):

    def __init__(self, emulators: list[Emulation],
                 requests_limit_same_emulator: int = 10,
                 change_emulator_on_error: bool = True,
                 **kwargs: Unpack["ClientConfig"]):
        super().__init__(**kwargs)
        self.emulators = emulators
        self.current_emulator_index = 0
        self.requests_limit_same_emulator = requests_limit_same_emulator
        self.change_emulator_on_error = change_emulator_on_error
        self.requests_made_with_current_emulator = 0

    def _get_next_emulator(self) -> Optional[Emulation]:
        if not self.emulators:
            return None
        
        emulator = self.emulators[self.current_emulator_index]
        self.current_emulator_index = (self.current_emulator_index + 1) % len(self.emulators)
        return emulator

    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:

            if not self.client:
                self.client = self._create_client(**self.client_configs)

            headers = kwargs.get("headers", {})

            current_emulator = self.emulators[self.current_emulator_index]
            self.client_configs['emulation'] = current_emulator
            self.client = self._create_client(**self.client_configs)

            start = time.time()
            res = self.client.request(method=method, url=url, **kwargs)
            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()
            self.requests_made_with_current_emulator += 1

            if self.requests_made_with_current_emulator >= self.requests_limit_same_emulator:
                self._get_next_emulator()
                self.requests_made_with_current_emulator = 0

            self._create_log(
                method=method,
                request_url=res.url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=None,
                emulation=current_emulator,
                headers=headers
            )

            return res
         

        except Exception as e:

            if self.change_emulator_on_error:
                self._get_next_emulator()
                self.requests_made_with_current_emulator = 0

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=None,
                emulation=current_emulator,
                headers=headers
            )

            raise RequestErrorException(e)  

class RNetMultiplesProxiesAndEmulatorsClient(RNetProxiesManagerClient):

    def __init__(self,
                 emulators: list[Emulation],
                 proxies_manager: ProxiesManager,
                 requests_limit_same_proxy: int = -1,
                 requests_limit_same_emulator: int = 10,
                 status_codes_to_change_proxy: list[int] = None,
                 status_codes_to_change_emulator: list[int] = None,
                 change_emulator_on_error: bool = True,
                 os_emulators: list[EmulationOS] = None,
                 **kwargs: Unpack["ClientConfig"]):
        
        super().__init__(proxies_manager,
                         requests_limit_same_proxy,
                         status_codes_to_change_proxy,
                         **kwargs)
        
        self.emulators = emulators
        self.os_emulators = os_emulators or []
        self.current_emulator_index = 0
        self.requests_limit_same_emulator = requests_limit_same_emulator
        self.change_emulator_on_error = change_emulator_on_error
        self.status_codes_to_changes_emulator = status_codes_to_change_emulator if status_codes_to_change_emulator else []
        self.requests_made_with_current_emulator = 0

    def _get_next_emulator(self) -> Optional[Emulation]:
        if not self.emulators:
            return None
        
        emulator = self.emulators[self.current_emulator_index]
        self.current_emulator_index = (self.current_emulator_index + 1) % len(self.emulators)
        return emulator
    

    def _get_emulation_os_for_emulator(self, emulator: Emulation) -> Optional[EmulationOS]:
        if not self.os_emulators:
            return None
        
        index = self.emulators.index(emulator) % len(self.os_emulators)
        return self.os_emulators[index]


    def _is_emulator_change_needed(self, status_code: int, requests_made_with_current_emulator: int) -> bool:

        if self.status_codes_to_changes_emulator and status_code in self.status_codes_to_changes_emulator:
            return True
        
        if requests_made_with_current_emulator >= self.requests_limit_same_emulator:
            return True
        
        return False
    
    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:
            current_emulator = self.emulators[self.current_emulator_index]

            if not self.client:
                current_emulator = self.emulators[self.current_emulator_index]
                self.client_configs['emulation'] = EmulationOption(self.emulators[self.current_emulator_index],
                                                                   emulation_os=self._get_emulation_os_for_emulator(current_emulator))
                self.client = self._create_client(**self.client_configs)

            start = time.time()
            headers = kwargs.get("headers", {})

        
            current_proxy: Proxy = self.proxies_manager.get_current_proxy()
            logger.debug(f"Using proxy: {current_proxy}")
       
            self.requests_made_with_current_emulator += 1

            if current_proxy:
                self.requests_made_with_current_proxy += 1
                res = self.client.request(method=method,
                                          url=url,
                                          proxy=ProxyRNet.all(current_proxy.get_proxy_url()),
                                          **kwargs)

            else:
                res = self.client.request(method=method, url=url, **kwargs)

            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()

            change_proxy = self._is_proxy_change_needed(
                status_code=status_code,
                requests_made_with_current_proxy=self.requests_made_with_current_proxy
            )

            if change_proxy:
                logger.debug(f"Changing proxy due to status code {status_code} "
                             f"or request limit reached ({self.requests_made_with_current_proxy}).")
                
                self.client = self._create_client(**self.client_configs)
                self.proxies_manager.get_next_proxy()
                self.requests_made_with_current_proxy = 0

            change_emulator = self._is_emulator_change_needed(
                status_code=status_code,
                requests_made_with_current_emulator=self.requests_made_with_current_emulator
            )

            if change_emulator:
                logger.debug(f"Changing emulator due to status code {status_code} "
                             f"or request limit reached ({self.requests_made_with_current_emulator}).")
                
                self._get_next_emulator()
                self.requests_made_with_current_emulator = 0
                self.client_configs['emulation'] =  EmulationOption(self.emulators[self.current_emulator_index],
                                                                   emulation_os=self._get_emulation_os_for_emulator(current_emulator))
                self.client = self._create_client(**self.client_configs)


            self._create_log(
                method=method,
                request_url=url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=current_emulator,
                headers=headers
            )

            return res
         

        except Exception as e:
            if not self.change_emulator_on_error:
                self.client = self._create_client(**self.client_configs)
                self.proxies_manager.get_next_proxy()
                self.requests_made_with_current_proxy = 0

            else:
                self._get_next_emulator()
                self.requests_made_with_current_emulator = 0
                self.client_configs['emulation'] = EmulationOption(self.emulators[self.current_emulator_index],
                                                                   emulation_os=self._get_emulation_os_for_emulator(current_emulator))
                self.client = self._create_client(**self.client_configs)

            logger.error(f"Request error occurred: {e}. Changed proxy and emulator and retrying next request.")

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=current_emulator,
                headers=headers)