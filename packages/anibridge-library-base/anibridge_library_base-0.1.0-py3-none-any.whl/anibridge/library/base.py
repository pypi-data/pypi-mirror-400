"""Library provider base classes and contracts."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, TypeVar, cast

from starlette.requests import Request

__all__ = [
    "HistoryEntry",
    "LibraryEntity",
    "LibraryEntry",
    "LibraryEpisode",
    "LibraryMedia",
    "LibraryMovie",
    "LibraryProvider",
    "LibraryProviderT",
    "LibrarySeason",
    "LibrarySection",
    "LibraryShow",
    "LibraryUser",
    "MediaKind",
]


LibraryProviderT = TypeVar("LibraryProviderT", bound="LibraryProvider", covariant=True)


class MediaKind(StrEnum):
    """Supported high-level media kinds within a library provider."""

    MOVIE = "movie"
    SHOW = "show"
    SEASON = "season"
    EPISODE = "episode"


@dataclass(slots=True, eq=False)
class LibraryEntity[ProviderT: LibraryProvider](ABC):
    """Base class for library entities."""

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
        """Return the entity title."""
        return self._title

    def __hash__(self) -> int:
        """Compute a hash based on provider namespace, class name, and key."""
        return hash((self._provider.NAMESPACE, self.__class__.__name__, self.key))

    def __eq__(self, other: object) -> bool:
        """Compare entities by provider namespace and key."""
        if other.__class__ is not self.__class__:
            return NotImplemented
        other_ent = cast(LibraryEntity, other)
        return (
            getattr(self._provider, "NAMESPACE", None)
            == getattr(other_ent._provider, "NAMESPACE", None)
            and self.key == other_ent.key
        )

    def __repr__(self) -> str:
        """Return a short representation for debugging."""
        return f"<{self.__class__.__name__}:{self.key}:{self.title[:32]}>"


class LibrarySection(LibraryEntity[LibraryProviderT], ABC):
    """Represents a logical collection/section within the media library."""


class LibraryMedia(LibraryEntity[LibraryProviderT], ABC):
    """Base class for library media items.

    Implementations should provide concrete behaviour for the abstract
    properties and methods below.
    """

    @property
    def external_url(self) -> str | None:
        """URL to the provider's media item, if available."""
        return None

    @property
    def poster_image(self) -> str | None:
        """Primary poster or cover image URL, if available."""
        return None

    def ids(self) -> dict[str, str]:
        """Return external identifier mappings for logging/debugging."""
        return {}


class LibraryEntry[ProviderT: LibraryProvider](LibraryEntity[ProviderT], ABC):
    """Base class for library entries."""

    @abstractmethod
    async def history(self) -> Sequence[HistoryEntry]:
        """Return user history entries for this media item (tz-aware timestamps)."""
        ...

    @abstractmethod
    def media(self) -> LibraryMedia[ProviderT]:
        """Return the media item associated with this entry."""
        ...

    @property
    @abstractmethod
    def on_watching(self) -> bool:
        """Whether the item is on the user's current watching list."""
        ...

    @property
    @abstractmethod
    def on_watchlist(self) -> bool:
        """Whether the item is on the user's watchlist."""
        ...

    @abstractmethod
    async def review(self) -> str | None:
        """Return the user's review text for this item, if any."""
        ...

    @abstractmethod
    def section(self) -> LibrarySection[LibraryProviderT]:
        """Return the parent library section for this media item."""
        ...

    @property
    def user_rating(self) -> int | None:
        """User rating on a 0-100 scale, or None if not rated."""
        return None

    @property
    @abstractmethod
    def view_count(self) -> int:
        """Total view count for the item (including children)."""
        ...


class LibraryMovie(LibraryEntry[LibraryProviderT], ABC):
    """Movie item in a media library."""


class LibraryShow(LibraryEntry[LibraryProviderT], ABC):
    """Episodic show/series in a media library."""

    @abstractmethod
    def episodes(self) -> Sequence[LibraryEpisode[LibraryProviderT]]:
        """Get child episodes belonging to the show.

        Returns:
            Sequence[LibraryEpisode]: Child episodes.
        """
        ...

    @abstractmethod
    def seasons(self) -> Sequence[LibrarySeason[LibraryProviderT]]:
        """Get child seasons belonging to the show.

        Returns:
            Sequence[LibrarySeason]: Child seasons.
        """
        ...


class LibrarySeason(LibraryEntry[LibraryProviderT], ABC):
    """Season container within a show."""

    index: int

    @abstractmethod
    def episodes(self) -> Sequence[LibraryEpisode[LibraryProviderT]]:
        """Get child episodes belonging to the season.

        Returns:
            Sequence[LibraryEpisode]: Child episodes.
        """
        ...

    @abstractmethod
    def show(self) -> LibraryShow[LibraryProviderT]:
        """Get the parent show of the season.

        Returns:
            LibraryShow: The parent show.
        """
        ...

    def __repr__(self) -> str:
        """Short representation including show title and season index."""
        return (
            f"<{self.__class__.__name__}:{self.key}:{self.show().title[:32]}>:"
            f"S{self.index:02d}"
        )


class LibraryEpisode(LibraryEntry[LibraryProviderT], ABC):
    """Episode item within a season/show."""

    index: int
    season_index: int

    @abstractmethod
    def season(self) -> LibrarySeason[LibraryProviderT]:
        """Get the parent season of the episode.

        Returns:
            LibrarySeason: The parent season.
        """
        ...

    @abstractmethod
    def show(self) -> LibraryShow[LibraryProviderT]:
        """Get the parent show of the episode.

        Returns:
            LibraryShow: The parent show.
        """
        ...

    def __repr__(self) -> str:
        """Short representation including show title, season and episode indexes."""
        return (
            f"<{self.__class__.__name__}:{self.key}:{self.show().title[:32]}>:"
            f"S{self.season_index:02d}E{self.index:02d}>"
        )


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    """User history event for a library item."""

    library_key: str
    viewed_at: datetime  # Must be timezone-aware


@dataclass(frozen=True, slots=True)
class LibraryUser:
    """User information for a library provider."""

    key: str
    title: str

    def __hash__(self) -> int:
        """Return a hash based on the user key."""
        return hash(self.key)


class LibraryProvider(ABC):
    """Abstract base provider that exposes a user media library."""

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
    async def get_sections(self) -> Sequence[LibrarySection[LibraryProviderT]]:
        """Return available library sections for the provider.

        Returns:
            Sequence[LibrarySection[LibraryProviderT]]: The available library sections.
        """
        ...

    @abstractmethod
    async def list_items(
        self,
        section: LibrarySection[LibraryProviderT],
        *,
        min_last_modified: datetime | None = None,
        require_watched: bool = False,
        keys: Sequence[str] | None = None,
    ) -> Sequence[LibraryEntry[LibraryProviderT]]:
        """List items in a library section with optional filtering.

        Args:
            section (LibrarySection[LibraryProviderT]): The library section to list
                items from.
            min_last_modified (datetime | None): If provided, only include items
                modified after this timezone-aware timestamp.
            require_watched (bool): If True, only include items marked as watched.
            keys (Sequence[str] | None): If provided, only include items whose keys are
                in this sequence.

        Returns:
            Sequence[LibraryEntry[LibraryProviderT]]: The list of library items.
        """
        ...

    async def parse_webhook(self, request: Request) -> tuple[bool, Sequence[str]]:
        """Parse an incoming webhook and return the affected item keys.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            tuple[bool, Sequence[str]]: A tuple where the first element indicates
                whether the webhook applies to the current provider, and the second
                element is a sequence of affected item keys.
        """
        return False, ()

    @abstractmethod
    def user(self) -> LibraryUser | None:
        """Return the associated user object, if any.

        Returns:
            LibraryUser | None: The associated user object, if any.
        """
        ...
