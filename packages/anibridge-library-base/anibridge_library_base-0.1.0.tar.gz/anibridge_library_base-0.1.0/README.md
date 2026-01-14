# anibridge-library-base

anibridge-library-base provides base classes and utilities to implement and register media library providers for the [AniBridge](https://github.com/anibridge/anibridge) project.

> [!IMPORTANT]
> This package is intended for developers building AniBridge library providers. If you're looking to use AniBridge as an end user, please refer to the [AniBridge documentation](https://anibridge.eliasbenb.dev/).

## Installation

```shell
pip install anibridge-library-base
# pip install git+https://github.com/anibridge/anibridge-library-base.git
```

## API reference

The package exposes core base classes in `anibridge.library.base` and registration helpers in `anibridge.library.registry`.

To get more context, read the `anibridge.library.base` and `anibridge.library.registry` module docstrings.

- `LibraryProvider` (base class)

  - Key methods and hooks:
    - `__init__(*, config: dict | None = None) -> None`: Construct a provider with optional configuration.
    - `async initialize() -> None`: Optional async initialization hook for I/O or authentication.
    - `async clear_cache() -> None`: Clear any provider caches to free memory or refresh data.
    - `async close() -> None`: Close the provider and release resources.
    - `async get_sections() -> Sequence[LibrarySection[LibraryProviderT]]`: Return available library sections for the provider.
    - `async list_items(section: LibrarySection[LibraryProviderT], *, min_last_modified: datetime | None = None, require_watched: bool = False, keys: Sequence[str] | None = None) -> Sequence[LibraryMedia[LibraryProviderT]]`: List media items within a section with optional filtering.
    - `async parse_webhook(request: Request) -> tuple[bool, Sequence[str]]`: Parse an incoming webhook and return whether it applies plus affected item keys.
    - `user() -> LibraryUser | None`: Return the associated user object, if any.

- `LibraryEntry` (per-item user state)

  - Key methods and properties:
    - `async history() -> Sequence[HistoryEntry]`: Return user history events for the item (tz-aware timestamps).
    - `media() -> LibraryMedia[LibraryProviderT]`: Return the associated `LibraryMedia` object.
    - `on_watching -> bool`: Whether the item is currently being watched.
    - `on_watchlist -> bool`: Whether the item is on the user's watchlist.
    - `async review() -> str | None`: Return the user's review text for the item, if any.
    - `section() -> LibrarySection[LibraryProviderT]`: Return the parent library section for the item.
    - `user_rating -> int | None`: Optional user rating on a 0–100 scale.
    - `view_count -> int`: Total view count for the item (including children).

- `LibraryMedia` (media metadata)

  - Key properties and helpers:
    - `external_url -> str | None`: URL to the provider's media item, if available.
    - `poster_image -> str | None`: Poster or cover image URL, if available.
    - `ids() -> dict[str, str]`: External identifier mappings for logging/debugging.

- `LibraryShow`, `LibrarySeason`, `LibraryEpisode`, `LibraryMovie`

  - `LibraryShow`:
    - `episodes() -> Sequence[LibraryEpisode[LibraryProviderT]]`: Return child episodes.
    - `seasons() -> Sequence[LibrarySeason[LibraryProviderT]]`: Return child seasons.
  - `LibrarySeason`:
    - `index: int`: Season index.
    - `episodes() -> Sequence[LibraryEpisode[LibraryProviderT]]`: Return episodes in the season.
    - `show() -> LibraryShow[LibraryProviderT]`: Return the parent show.
  - `LibraryEpisode`:
    - `index: int`, `season_index: int`: Episode and season indices.
    - `season() -> LibrarySeason[LibraryProviderT]`: Return parent season.
    - `show() -> LibraryShow[LibraryProviderT]`: Return parent show.

- `HistoryEntry`

  - `library_key: str`, `viewed_at: datetime` — records a timezone-aware view event for an item.

- `MediaKind` (StrEnum)

  - High-level media kinds: `MOVIE`, `SHOW`, `SEASON`, `EPISODE`.

- `LibraryProviderRegistry` and `library_provider` decorator

  - Registry API (see `anibridge.library.registry`):
    - `create(namespace: str, *, config: dict | None = None) -> LibraryProvider`: Instantiate a provider for `namespace`.
    - `get(namespace: str) -> type[LibraryProvider]`: Return the provider class registered under `namespace`.
    - `namespaces() -> tuple[str, ...]`: Return registered namespace identifiers.
    - `register(provider_cls: type[LibraryProvider] | None = None, *, namespace: str | None = None) -> type[LibraryProvider] | Callable[[type[LP]], type[LP]]`: Register a provider class or act as a decorator factory.
    - `unregister(namespace: str) -> None`: Remove a provider registration.
    - `provider_registry`: Module-level registry instance.
    - `library_provider(...)`: Convenience decorator to register providers into the module-level registry.

## Examples

You can view the following built-in provider implementations as examples of how to implement the base classes:

- [anibridge-provider-template](https://github.com/anibridge/anibridge-provider-template)
- [anibridge-plex-provider](https://github.com/anibridge/anibridge-plex-provider)
