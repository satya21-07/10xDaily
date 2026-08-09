from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class HealthDataSource(ABC):
    """Base class for health data sources."""
    
    @abstractmethod
    def fetch_data(self, topic: str) -> Optional[Dict[str, Any]]:
        """Fetch data from the source."""
        pass
    
    @abstractmethod
    def get_source_metadata(self) -> Dict[str, str]:
        """Return metadata about the source."""
        pass
