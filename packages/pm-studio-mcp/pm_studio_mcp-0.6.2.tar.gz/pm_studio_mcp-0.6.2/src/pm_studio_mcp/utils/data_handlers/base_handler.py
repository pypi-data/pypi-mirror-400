from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class BaseHandler(ABC):
    @abstractmethod
    def fetch_data(self, product_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Handle the data center operation.
        This method should be overridden by subclasses.
        """
        pass