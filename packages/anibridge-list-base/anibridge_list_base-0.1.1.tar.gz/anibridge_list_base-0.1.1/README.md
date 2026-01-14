# anibridge-list-base

anibridge-list-base provides base classes and utilities to implement and register media list providers for the [AniBridge](https://github.com/anibridge/anibridge) project.

> [!IMPORTANT]
> This package is intended for developers building AniBridge list providers. If you're looking to use AniBridge as an end user, please refer to the [AniBridge documentation](https://anibridge.eliasbenb.dev/).

## Installation

```shell
pip install anibridge-list-base
# pip install git+https://github.com/anibridge/anibridge-list-base.git
```

## API reference

The library exposes concrete base classes in `anibridge.list.base` and registration helpers in `anibridge.list.registry`.

To get some more context, explore the `anibridge.list.base` module's source code and docstrings.

- `ListProvider` (base class)

  - Key methods and hooks:
    - `async backup_list() -> str`: Optional backup hook returning a string representation of the user's list that can be restored later via `restore_list()`.
    - `async build_entry(key: str) -> ListEntry`: Prepare a `ListEntry` for a media item even if it's not yet in the user's list.
    - `async clear_cache() -> None`: Optional cache clearing hook that AniBridge will occasionally run to free up memory and prevent stale data.
    - `async close() -> None`: Optional cleanup hook called when the provider is shut down or reloaded.
    - `async delete_entry(key: str) -> None`: Delete a list entry.
    - `async get_entries_batch(keys: Sequence[str]) -> Sequence[ListEntry | None]`: Optional batch helper to fetch multiple entries at once.
    - `async get_entry(key: str) -> ListEntry | None`: Fetch a user's list entry; return `None` if not present.
    - `async initialize() -> None`: Optional async initialization called once after construction. Perform network I/O, authentication, or pre-fetching here.
    - `resolve_mappings(mapping: MappingGraph, *, scope: str | None) -> MappingDescriptor | None`: Resolve a media identifier from a mapping graph to a provider descriptor. If `scope` is provided, prefer descriptors matching that scope.
    - `async restore_list(backup: str) -> None`: Optional backup restore hook. If a provider does not support backups, `restore_list()` raises `NotImplementedError`.
    - `async search(query: str) -> Sequence[ListEntry]`: Optional search helper returning matching entries.
    - `async update_entries_batch(entries: Sequence[ListEntry]) -> Sequence[ListEntry | None]`: Optional batch helper to update multiple entries at once.
    - `async update_entry(key: str, entry: ListEntry) -> ListEntry | None`: Update an entry; return the updated entry or `None` on failure.

- `ListEntry`, `ListMedia`, `ListUser` (base classes)

  - `ListEntry` stores and exposes properties and setters for `progress`, `repeats`, `review`, `status` (`ListStatus`), `user_rating`, `started_at`, `finished_at`, and `total_units`, plus a `media()` method returning the associated `ListMedia`.
  - `ListMedia` stores `media_type` (`ListMediaType`), optional `labels`, `poster_image`, `external_url`, and `total_units`.
  - `ListUser` is an immutable dataclass with `key` and `title`.
  - `user_rating` is a 0–100 integer scale (providers may document their own mapping).

- `ListStatus` (StrEnum)

  - Enum of common list statuses: `COMPLETED`, `CURRENT`, `DROPPED`, `PAUSED`, `PLANNING`, `REPEATING`.
  - Includes ordering semantics via `priority` for comparison.

- Mapping protocols

  - `MappingDescriptor`, `MappingEdge`, `MappingGraph` describe how media identifiers can be related and provide a hook for providers to resolve identifiers from a graph of mappings.
  - `MappingDescriptor` exposes `provider`, `entry_id`, `scope` attributes and a `key()` helper method; providers should pick a descriptor they can resolve and return it from `resolve_mappings()`.

- `ListProviderRegistry` and `list_provider` decorator
  - `ListProviderRegistry` is a simple registry that maps namespace strings to provider classes. Use `create(namespace, *, config=None)` to instantiate a provider or `get(namespace)` to access the class.
  - `list_provider` is a decorator helper that registers a provider with the module-level `provider_registry` by default.

## Examples

You can view the following built-in provider implementations as examples of how to implement the base classes:

- [anibridge-provider-template](https://github.com/anibridge/anibridge-provider-template)
- [anibridge-anilist-provider](https://github.com/anibridge/anibridge-anilist-provider)
- [anibridge-mal-provider](https://github.com/anibridge/anibridge-mal-provider)
