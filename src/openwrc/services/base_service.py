from typing import Optional
from openwrc.storage.data_store_service import WrcDataStore


class BaseService:
    def __init__(self, data_store: Optional[WrcDataStore] = None) -> None:
        self.data_store = data_store or WrcDataStore()
