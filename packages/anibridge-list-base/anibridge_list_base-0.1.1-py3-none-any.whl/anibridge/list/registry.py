"""Registration utilities for `ListProvider` implementations."""

from collections.abc import Callable, Iterator
from typing import TypeVar, overload

from anibridge.list.base import ListProvider

LP = TypeVar("LP", bound=ListProvider)


class ListProviderRegistry:
    """Registry for `ListProvider` implementations."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._providers: dict[str, type[ListProvider]] = {}

    def clear(self) -> None:
        """Remove all provider registrations."""
        self._providers.clear()

    def create(self, namespace: str, *, config: dict | None = None) -> ListProvider:
        """Instantiate the provider registered under `namespace`.

        Args:
            namespace (str): The namespace identifier to create.
            config (dict | None): Optional configuration dictionary to pass to the
                provider constructor.

        Returns:
            ListProvider: An instance of the registered provider.
        """
        provider_cls = self.get(namespace)
        return provider_cls(config=config)

    def get(self, namespace: str) -> type[ListProvider]:
        """Return the provider class registered under `namespace`.

        Args:
            namespace (str): The namespace identifier to look up.

        Returns:
            type[ListProvider]: The registered provider class.
        """
        try:
            return self._providers[namespace]
        except KeyError as exc:
            raise LookupError(
                f"No provider registered for namespace '{namespace}'."
            ) from exc

    def namespaces(self) -> tuple[str, ...]:
        """Return a tuple of registered namespace identifiers.

        Returns:
            tuple[str, ...]: The registered namespace identifiers.
        """
        return tuple(self._providers)

    @overload
    def register(
        self,
        provider_cls: type[LP],
        *,
        namespace: str | None = None,
    ) -> type[LP]: ...

    @overload
    def register(
        self,
        provider_cls: None = None,
        *,
        namespace: str | None = None,
    ) -> Callable[[type[LP]], type[LP]]: ...

    def register(
        self,
        provider_cls: type[LP] | None = None,
        *,
        namespace: str | None = None,
    ) -> type[LP] | Callable[[type[LP]], type[LP]]:
        """Register a provider class, optionally used as a decorator.

        Args:
            provider_cls (type[LP] | None): The provider class to register. If `None`,
                the method acts as a decorator factory.
            namespace (str | None): Explicit namespace override. Defaults to the class'
                `NAMESPACE` attribute.

        Returns:
            type[LP] | Callable[[type[LP]], type[LP]]: The registered provider class, or
                a decorator that registers the class.
        """

        def decorator(cls: type[LP]) -> type[LP]:
            """Register `cls` as a provider."""
            resolved_namespace = namespace or getattr(cls, "NAMESPACE", None)
            if not isinstance(resolved_namespace, str) or not resolved_namespace:
                raise ValueError(
                    "List providers must define a non-empty string `NAMESPACE` "
                    "attribute or pass `namespace=` when registering."
                )

            existing = self._providers.get(resolved_namespace)
            if existing is not None and existing is not cls:
                raise ValueError(
                    f"A provider is already registered for namespace "
                    f"'{resolved_namespace}'."
                )

            self._providers[resolved_namespace] = cls
            return cls

        if provider_cls is None:
            return decorator
        return decorator(provider_cls)

    def unregister(self, namespace: str) -> None:
        """Remove a provider registration if it exists.

        Args:
            namespace (str): The namespace identifier to unregister.
        """
        self._providers.pop(namespace, None)

    def __contains__(self, namespace: object) -> bool:
        """Check if a provider is registered under `namespace`."""
        return isinstance(namespace, str) and namespace in self._providers

    def __iter__(self) -> Iterator[tuple[str, type[ListProvider]]]:
        """Iterate over `(namespace, provider_class)` pairs."""
        return iter(self._providers.items())


provider_registry = ListProviderRegistry()


@overload
def list_provider[LP: ListProvider](
    cls: type[LP],
    *,
    namespace: str | None = None,
    registry: ListProviderRegistry | None = None,
) -> type[LP]: ...


@overload
def list_provider(
    cls: None = None,
    *,
    namespace: str | None = None,
    registry: ListProviderRegistry | None = None,
) -> Callable[[type[LP]], type[LP]]: ...


def list_provider[LP: ListProvider](
    cls: type[LP] | None = None,
    *,
    namespace: str | None = None,
    registry: ListProviderRegistry | None = None,
) -> type[LP] | Callable[[type[LP]], type[LP]]:
    """Class decorator that registers `ListProvider` implementations.

    This helper lets third-party providers register themselves declaratively:

        ```
        from anibridge.list import list_provider


        @list_provider(namespace="anilist")
        class AnilistListProvider:
            NAMESPACE = "anilist"
            ...
        ```

    Args:
        cls (type[LP] | None): The provider class to register. If `None`, the function
            acts as a decorator factory.
        namespace (str | None): Explicit namespace override. Defaults to the class'
            `NAMESPACE` attribute.
        registry (ListProviderRegistry | None): Alternate registry to insert into.
            Defaults to the module-level one.

    Returns:
        type[LP] | Callable[[type[LP]], type[LP]]: The registered provider class, or
            a decorator that registers the class.
    """
    active_registry = registry or provider_registry
    return active_registry.register(cls, namespace=namespace)
