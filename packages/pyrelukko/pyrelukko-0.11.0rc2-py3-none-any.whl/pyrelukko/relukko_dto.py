"""
Pyrelukko module for the dataclass RelukkoDTO
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Union, Any
from uuid import UUID
import json


@dataclass(frozen=True)
class RelukkoDTO:
    """Data Transfer Object representing a Relukko lock.
    
    Contains all metadata associated with a lock including identifiers,
    creator information, network details, and timestamps. Instances are
    immutable once created and support dict-like access patterns.
    """
    id: UUID
    lock_name: str
    creator: str
    ip: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Validate and convert field types after initialization.
        
        Ensures that id is a UUID and timestamps are datetime objects,
        converting from strings if necessary.
        
        :raises ValueError: If field values cannot be converted to expected types
        """
        # Convert id to UUID if needed
        if not isinstance(self.id, UUID):
            object.__setattr__(self, 'id', self._parse_uuid(self.id))

        # Convert timestamps to datetime if needed
        if not isinstance(self.expires_at, datetime):
            object.__setattr__(self, 'expires_at', self._parse_datetime(self.expires_at))

        if not isinstance(self.created_at, datetime):
            object.__setattr__(self, 'created_at', self._parse_datetime(self.created_at))

        if not isinstance(self.updated_at, datetime):
            object.__setattr__(self, 'updated_at', self._parse_datetime(self.updated_at))

    def __getitem__(self, key: str) -> Any:
        """Enable dict-like access using square brackets.
        
        :param key: Field name to access
        :type key: str
        :return: Field value
        :rtype: Any
        :raises KeyError: If key is not a valid field name
        """
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(f"'{key}' is not a valid field") from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get field value with optional default.
        
        :param key: Field name to access
        :type key: str
        :param default: Default value if key doesn't exist
        :type default: Any
        :return: Field value or default
        :rtype: Any
        """
        try:
            return self[key]
        except KeyError:
            return default

    @staticmethod
    def _parse_datetime(value: Union[str, datetime]) -> datetime:
        """Parse a datetime value from string or datetime object.
        
        :param value: ISO datetime string or datetime object
        :type value: Union[str, datetime]
        :return: Parsed datetime object
        :rtype: datetime
        :raises ValueError: If string cannot be parsed as ISO datetime
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Expected str or datetime, got {type(value)}")

    @staticmethod
    def _parse_uuid(value: Union[str, UUID]) -> UUID:
        """Parse a UUID value from string or UUID object.
        
        :param value: UUID string or UUID object
        :type value: Union[str, UUID]
        :return: Parsed UUID object
        :rtype: UUID
        :raises ValueError: If string cannot be parsed as UUID
        """
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            return UUID(value)
        raise ValueError(f"Expected str or UUID, got {type(value)}")

    @classmethod
    def from_dict(cls, data: dict) -> 'RelukkoDTO':
        """Create a RelukkoDTO instance from a dictionary.

        :param data: Dictionary containing lock data from the API
        :type data: dict
        :return: RelukkoDTO instance
        :rtype: RelukkoDTO
        """
        return cls(
            id=data['id'],
            lock_name=data['lock_name'],
            creator=data['creator'],
            ip=data['ip'],
            expires_at=data['expires_at'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )

    def to_dict(self) -> dict:
        """Convert the RelukkoDTO instance to a dictionary.

        :return: Dictionary representation of the lock data with string representations
        :rtype: dict
        """
        return {
            'id': str(self.id),
            'lock_name': self.lock_name,
            'creator': self.creator,
            'ip': self.ip,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __str__(self) -> str:
        """Return JSON string representation of the RelukkoDTO.
        
        :return: JSON string representation
        :rtype: str
        """
        return json.dumps(self.to_dict(), indent=2)
