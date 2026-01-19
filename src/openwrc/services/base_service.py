from typing import Optional
from openwrc.clients.wrc_api_client import WrcApiClient


class BaseService:
    def __init__(self, external_api_client: Optional[WrcApiClient] = None) -> None:
        self.external_api_client = external_api_client or WrcApiClient()
