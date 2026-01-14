"""Scope implementation for scoped service resolution."""

from typing import TYPE_CHECKING, TypeVar

from j2_ioc.errors.missing_dependency_error import MissingDependencyError

if TYPE_CHECKING:
    from j2_ioc.container import Container

T = TypeVar("T")


class Scope:
    """
    Scoped container for resolving scoped services.

    Use as a context manager:
        with container.scope() as scope:
            service = scope.resolve(MyService)
    """

    def __init__(self, container: "Container"):
        self._container = container
        self._scoped_cache: dict[type, object] = {}

    def __enter__(self) -> "Scope":
        return self

    def __exit__(self, *args: object) -> None:
        self._scoped_cache.clear()

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service within this scope."""
        return self._container._resolve(service_type, self._scoped_cache, set())

    def resolve_optional(self, service_type: type[T]) -> T | None:
        """Resolve a service or return None if not registered."""
        try:
            return self.resolve(service_type)
        except MissingDependencyError:
            return None
