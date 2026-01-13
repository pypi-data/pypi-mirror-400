from abc import ABC, abstractmethod
from typing import Optional
from ..models.delegation import DelegationSession

class BaseBackend(ABC):
    """
    Base class for delegation backends.
    """
    
    @abstractmethod
    async def spawn(self, session: DelegationSession) -> str:
        """
        Spawns the delegated task and returns a connection string or identifier.
        """
        pass

    @abstractmethod
    async def cleanup(self, session: DelegationSession):
        """
        Cleans up resources associated with the session.
        """
        pass
