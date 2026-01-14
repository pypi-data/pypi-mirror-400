"""List provider base classes and contracts."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from functools import total_ordering
from typing import ClassVar, Protocol, Self, TypeVar, cast

__all__ = [
    "ListEntity",
    "ListEntry",
    "ListMedia",
    "ListMediaType",
    "ListProvider",
    "ListProviderT",
    "ListStatus",
    "ListUser",
    "MappingDescriptor",
    "MappingEdge",
    "MappingGraph",
]


ListProviderT = TypeVar("ListProviderT", bound="ListProvider", covariant=True)


class MappingDescriptor(Protocol):
    """Protocol for a mapping descriptor used in resolving media keys."""

    provider: str
    entry_id: str
    scope: str

    def key(self) -> str:
        """Get the unique key for this mapping descriptor.

        Returns:
            str: The unique key.
        """
        ...


class MappingEdge(Protocol):
    """Protocol for a mapping edge used in resolving media keys."""

    source: MappingDescriptor
    destination: MappingDescriptor
    source_range: str
    destination_range: str | None


class MappingGraph(Protocol):
    """Protocol for a mapping graph used in resolving media keys."""

    edges: tuple[MappingEdge, ...]

    def descriptors(self) -> tuple[MappingDescriptor, ...]:
        """Get unique descriptors referenced by the edges.

        Returns:
            Sequence[MappingDescriptor]: The unique mapping descriptors.
        """
        ...


class ListMediaType(StrEnum):
    """Supported media types in a list."""

    TV = "TV"
    MOVIE = "MOVIE"


@total_ordering
class ListStatus(StrEnum):
    """Supported statuses for media items in a list."""

    COMPLETED = "completed"
    CURRENT = "current"
    DROPPED = "dropped"
    PAUSED = "paused"
    PLANNING = "planning"
    REPEATING = "repeating"

    __PRIORITY: ClassVar[dict[str, int]] = {
        "completed": 3,
        "repeating": 3,
        "current": 2,
        "paused": 2,
        "dropped": 2,
        "planning": 1,
    }

    @property
    def priority(self) -> int:
        """Get the priority of the ListStatus for comparison purposes."""
        return self.__PRIORITY[self.value]

    def __eq__(self, other: object) -> bool:
        """Check equality with another ListStatus (not based on priority)."""
        if not isinstance(other, ListStatus):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        """Check if this ListStatus has lower priority than another."""
        if not isinstance(other, ListStatus):
            return NotImplemented
        return self.priority < other.priority

    def __le__(self, other: object) -> bool:
        """Check if this ListStatus has lower or equal priority than another."""
        if not isinstance(other, ListStatus):
            return NotImplemented
        return self.priority <= other.priority


@dataclass(frozen=True, slots=True)
class ListUser:
    """User information for a list provider."""

    key: str
    title: str = field(compare=False)


@dataclass(slots=True, eq=False)
class ListEntity[ProviderT: ListProvider](ABC):
    """Base class for list entities."""

    _provider: ProviderT = field(repr=False, compare=False)
    _key: str
    _title: str = field(compare=False)

    @property
    def key(self) -> str:
        """Return the unique key for this entity."""
        return self._key

    def provider(self) -> ProviderT:
        """Return the provider associated with this entity."""
        return self._provider

    @property
    def title(self) -> str:
        """Return the title of this entity."""
        return self._title

    def __hash__(self) -> int:
        """Compute a hash based on the provider namespace, class name, and key."""
        return hash((self._provider.NAMESPACE, self.__class__.__name__, self.key))

    def __eq__(self, other: object) -> bool:
        """Check equality with another ListEntity based on provider and key."""
        if other.__class__ is not self.__class__:
            return NotImplemented
        other_ent = cast(ListEntity, other)
        return (
            self._provider.NAMESPACE == other_ent._provider.NAMESPACE
            and self.key == other_ent.key
        )

    def __repr__(self) -> str:
        """Return a string representation of the ListEntity."""
        return (
            f"<{self.__class__.__name__}:{self._provider.NAMESPACE}:{self.key}:"
            f"{self.title[:32]}>"
        )


class ListMedia[ProviderT: ListProvider](ListEntity[ProviderT], ABC):
    """Base class for media items in a provider list.

    Subclasses should call the base constructor and may override properties if
    they need custom behaviour; defaults store values provided at init time.
    """

    @property
    def external_url(self) -> str | None:
        """URL to the provider's media item, if available."""
        return None

    @property
    def labels(self) -> Sequence[str]:
        """Display labels such as season or release year."""
        return ()

    @abstractmethod
    @property
    def media_type(self) -> ListMediaType:
        """Type of media (e.g., TV, MOVIE)."""
        ...

    @property
    def poster_image(self) -> str | None:
        """Poster or cover image URL, if provided by the provider."""
        return None

    @abstractmethod
    @property
    def total_units(self) -> int | None:
        """Total number of units (episodes/chapters) for the media."""
        ...


class ListEntry[ProviderT: ListProvider](ListEntity[ProviderT], ABC):
    """Base class for list entries for a given media item."""

    @abstractmethod
    @property
    def progress(self) -> int | None:
        """Progress integer (e.g., episodes watched)."""
        ...

    @abstractmethod
    @progress.setter
    def progress(self, value: int | None) -> None: ...

    @abstractmethod
    @property
    def repeats(self) -> int | None:
        """Repeat count for the entry."""
        ...

    @abstractmethod
    @repeats.setter
    def repeats(self, value: int | None) -> None: ...

    @abstractmethod
    @property
    def review(self) -> str | None:
        """User review text, if any."""
        ...

    @abstractmethod
    @review.setter
    def review(self, value: str | None) -> None: ...

    @abstractmethod
    @property
    def status(self) -> ListStatus | None:
        """Watch status for the entry."""
        ...

    @abstractmethod
    @status.setter
    def status(self, value: ListStatus | None) -> None:
        """Update the status for the entry."""
        ...

    @abstractmethod
    @property
    def user_rating(self) -> int | None:
        """User rating on a 0-100 scale."""
        ...

    @abstractmethod
    @user_rating.setter
    def user_rating(self, value: int | None) -> None:
        """Update the user rating for the entry."""
        ...

    @abstractmethod
    @property
    def started_at(self) -> datetime | None:
        """Timestamp when the user started the entry (timezone-aware)."""
        ...

    @abstractmethod
    @started_at.setter
    def started_at(self, value: datetime | None) -> None:
        """Update the started_at timestamp for the entry."""
        ...

    @abstractmethod
    @property
    def finished_at(self) -> datetime | None:
        """Timestamp when the user first completed the entry (timezone-aware)."""
        ...

    @abstractmethod
    @finished_at.setter
    def finished_at(self, value: datetime | None) -> None:
        """Update the finished_at timestamp for the entry."""
        ...

    @abstractmethod
    def media(self) -> ListMedia[ProviderT]:
        """Return the media item associated with this entry."""
        ...


class ListProvider(ABC):
    """Abstract base provider that exposes a user media list."""

    NAMESPACE: ClassVar[str]

    def __init__(self, *, config: dict | None = None) -> None:
        """Initialize the provider with optional configuration.

        Args:
            config (dict | None): Any configuration options that were detected with the
                provider's namespace as a prefix.
        """
        return None

    async def initialize(self) -> None:
        """Asynchronous initialization hook.

        Put any async logic that should be run after construction here.
        """
        return None

    async def backup_list(self) -> str:
        """Backup the entire list from the provider.

        It is up to the implementation to decide the format of the backup data. Whatever
        format, it should be serializable/deserializable as a string.

        Backup capabilities are optional. If a provider does not support backups, this
        method should raise a NotImplementedError.

        Returns:
            str: A serialized string representation of all list entries.
        """
        raise NotImplementedError(f"{self.NAMESPACE} does not support backup_list()")

    @abstractmethod
    async def build_entry(self, key: str) -> ListEntry[Self]:
        """Construct a list entry for the supplied media key.

        Implementations must return a list entry instance suitable for creating or
        updating a record, even if the user does not currently have the media in
        their list. This typically involves fetching provider metadata for the
        media and wrapping it with the provider's `ListEntry` implementation.

        Args:
            key (str): The unique key of the media item to prepare an entry for.

        Returns:
            ListEntry: The prepared list entry instance.
        """
        ...

    async def clear_cache(self) -> None:
        """Clear any cached data held by the provider.

        For more efficient implementations, it is a good idea to cache data
        fetched from the provider to minimize network requests. AniBridge uses
        this method occasionally to clear such caches.
        """
        return None

    async def close(self) -> None:
        """Close the provider and release resources."""
        return None

    @abstractmethod
    async def delete_entry(self, key: str) -> None:
        """Delete a list entry by its media key.

        Args:
            key (str): The unique key of the media item to delete.
        """
        ...

    @abstractmethod
    async def get_entry(self, key: str) -> ListEntry[Self] | None:
        """Retrieve a list entry by its media key.

        Args:
            key (str): The unique key of the media item to retrieve.

        Returns:
            ListEntry | None: The list entry if found, otherwise None.
        """
        ...

    async def get_entries_batch(
        self, keys: Sequence[str]
    ) -> Sequence[ListEntry[Self] | None]:
        """Retrieve multiple list entries by their media keys.

        The order of the returned sequence must match the order of the input keys.

        Args:
            keys (Sequence[str]): The unique keys of the media items to retrieve.

        Returns:
            Sequence[ListEntry | None]: A sequence of list entries, with None for any
                not found.
        """
        entries: list[ListEntry[Self] | None] = []
        for key in keys:
            entry = await self.get_entry(key)
            entries.append(entry)
        return entries

    @abstractmethod
    def resolve_mappings(
        self,
        mapping: MappingGraph,
        *,
        scope: str | None = None,
    ) -> MappingDescriptor | None:
        """Select a list media key from the supplied mapping graph.

        Implementations must choose some mapping descriptor from the graph that
        they can resolve to a media key.

        If a scope is provided, implementations should prefer descriptors
        matching that scope.

        Args:
            mapping (MappingGraph): Available mapping edges and descriptors.
            scope (str | None): Optional scope hint (e.g., "movie", "s1").

        Returns:
            MappingDescriptor | None: The resolved mapping descriptor, or None if
                no suitable descriptor could be found.
        """
        ...

    async def restore_list(self, backup: str) -> None:
        """Restore list entries from a backup string.

        The format of the backup string is determined by the implementation
        of `backup_list`.

        Args:
            backup (str): The serialized string representation of the list entries.
        """
        return None

    async def search(self, query: str) -> Sequence[ListEntry[Self]]:
        """Search the provider for entries matching the query.

        Args:
            query (str): The search query string.

        Returns:
            Sequence[ListEntry]: A sequence of matching list entries.
        """
        return []

    @abstractmethod
    async def update_entry(
        self, key: str, entry: ListEntry[Self]
    ) -> ListEntry[Self] | None:
        """Update a list entry with new information.

        Args:
            key (str): The unique key of the media item to update.
            entry (ListEntry): The updated entry information.

        Returns:
            ListEntry | None: The updated list entry, or None if the update failed.
        """
        ...

    async def update_entries_batch(
        self, entries: Sequence[ListEntry[Self]]
    ) -> Sequence[ListEntry[Self] | None]:
        """Update multiple list entries in a single operation.

        Args:
            entries (Sequence[ListEntry]): The list entries to update.

        Returns:
            Sequence[ListEntry | None]: A sequence of updated list entries, with None
                for any that could not be updated.
        """
        updated_entries: list[ListEntry[Self] | None] = []
        for entry in entries:
            updated_entry = await self.update_entry(entry.media().key, entry)
            updated_entries.append(updated_entry)
        return updated_entries

    @abstractmethod
    def user(self) -> ListUser | None:
        """Return the associated user object, if any.

        Returns:
            User | None: The associated user object, if any.
        """
        ...
