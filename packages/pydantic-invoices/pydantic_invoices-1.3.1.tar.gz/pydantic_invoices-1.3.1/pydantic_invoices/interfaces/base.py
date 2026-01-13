from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

M = TypeVar("M")
C = TypeVar("C")


class BaseRepository(ABC, Generic[M, C]):
    """Abstract base repository interface."""

    @abstractmethod
    def create(self, entity: C) -> M:
        """Create a new entity."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[M]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[M]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    def update(self, entity: M) -> M:
        """Update an entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        pass
