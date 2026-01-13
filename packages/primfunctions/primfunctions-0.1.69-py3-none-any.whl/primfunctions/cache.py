from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar


# TypeVar for generic typing of CachableEntity subclasses.
# Used in methods like cache_get to ensure type safety when deserializing cached entities.
# Example: cache_get(key, MyEntity) returns MyEntity, not just CachableEntity.
CachableEntityType = TypeVar('CachableEntityType', bound='CachableEntity')


class CachableEntity(ABC):
    """Abstract base class for entities that can be cached on the voicerun context.

    Defines the interface that must be implemented for proper caching support:
    - from_dict: Deserialize instance from cached dict
    - to_cache: Serialize instance to dict for caching
    """

    @classmethod
    @abstractmethod
    def from_cache(cls, data: Dict[str, Any]):
        """
        Deserialize entity from cached dict.

        Args:
            data: Serialized dict from cache

        Returns:
            Instance of the cachable entity
        """
        pass

    @abstractmethod
    def to_cache(self) -> Dict[str, Any]:
        """
        Serialize entity to dict for caching.

        Returns:
            Dict representation suitable for JSON serialization
        """
        pass
