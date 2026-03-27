"""
Abstract repository interfaces — module boundaries enforced here.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]: ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]: ...

    @abstractmethod
    async def create(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity_id: str, entity: T) -> Optional[T]: ...

    @abstractmethod
    async def delete(self, entity_id: str) -> bool: ...