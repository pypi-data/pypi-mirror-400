"""IoC Container implementation.

Features:
- Constructor injection via type hints
- Lifetime management (transient, scoped, singleton)
- Decorator pattern support
- Factory registration
- Circular dependency detection
- Protocol and ABC support
"""

import inspect
from collections.abc import Callable
from typing import Any, TypeVar, get_type_hints, cast
from python_ioc._service_descriptor import _ServiceDescriptor
from python_ioc.errors.circular_dependency_error import CircularDependencyError
from python_ioc.errors.container_error import ContainerError
from python_ioc.errors.missing_dependency_error import MissingDependencyError
from python_ioc.lifetime import Lifetime
from python_ioc.scope import Scope

T = TypeVar("T")


class Container:
    """
    IoC container with constructor injection.

    Example:
        container = (
            Container()
            .singleton(Config, AppConfig)
            .scoped(UserRepository, PostgresUserRepository)
            .transient(EmailSender, SmtpEmailSender)
            .decorate(UserRepository, CachedUserRepository)
        )

        with container.scope() as scope:
            sender = scope.resolve(EmailSender)
    """

    def __init__(self) -> None:
        self._descriptors: dict[type, _ServiceDescriptor] = {}
        self._singletons: dict[type, object] = {}

    def transient(
        self,
        service_type: type[T],
        implementation: type[T] | Callable[..., T] | None = None,
    ) -> "Container":
        """Register a class with 'transient' lifetime."""
        return self._register(service_type, implementation, Lifetime.TRANSIENT)

    def scoped(
        self,
        service_type: type[T],
        implementation: type[T] | Callable[..., T] | None = None,
    ) -> "Container":
        """Register a class with 'scoped' lifetime."""
        return self._register(service_type, implementation, Lifetime.SCOPED)

    def singleton(
        self,
        service_type: type[T],
        implementation: type[T] | Callable[..., T] | None = None,
    ) -> "Container":
        """Register a class with 'singleton' lifetime."""
        return self._register(service_type, implementation, Lifetime.SINGLETON)

    def instance(self, service_type: type[T], obj: T) -> "Container":
        """Register an existing instance as a singleton"""
        self._descriptors[service_type] = _ServiceDescriptor(
            service_type=service_type, instance=obj, lifetime=Lifetime.SINGLETON
        )
        self._singletons[service_type] = obj
        return self

    def factory(
        self,
        service_type: type[T],
        factory_fn: Callable[..., T],
        lifetime: Lifetime = Lifetime.TRANSIENT,
    ) -> "Container":
        """
        Register a factory function for creating instances.

        The factory can request dependencies via type hints:
            container.factory(
                Connection,
                lambda config: Config: psycopg.connect(config.db_url)
            )

        Or use a regular function:
            def create_connection(config: Config) -> Connection:
                return psycopg.connect(config.db_url)

            container.factory(Connection, create_connection)
        """
        self._descriptors[service_type] = _ServiceDescriptor(
            service_type=service_type, factory=factory_fn, lifetime=lifetime
        )
        return self

    def decorate(self, service_type: type[T], decorator_type: type[T]) -> "Container":
        """
        Add a decorator around a service.

        Decorators wrap the original service. Multiple decorators are applied
        in registration order (first registered = outermost).

        The decorator must accept the decorated service as its first constructor
        argument (by type hint).

        Example:
            class CachedUserRepository(UserRepository):
                def __init__(self, inner: UserRepository, cache: Cache):
                    self.inner = inner
                    self.cache = cache

                def get(self, user_id: int) -> dict:
                    if user_id in self.cache:
                        return self.cache[user_id]
                    result = self.inner.get(user_id)
                    self.cache[user_id] = result
                    return result

            container.decorate(UserRepository, CachedUserRepository)
        """
        if service_type not in self._descriptors:
            raise ConnectionError(
                f"Cannot decorate '{service_type.__name__}': not registered"
                "Register the service before applying decorators."
            )
        self._descriptors[service_type].decorators.append(decorator_type)
        return self

    def _register(
        self,
        service_type: type,
        implementation: type | Callable | None,
        lifetime: Lifetime,
    ) -> "Container":
        impl = implementation or service_type

        if callable(impl) and not isinstance(impl, type):
            descriptor = _ServiceDescriptor(
                service_type=service_type, factory=impl, lifetime=lifetime
            )
        else:
            descriptor = _ServiceDescriptor(
                service_type=service_type, implementation=impl, lifetime=lifetime
            )
        self._descriptors[service_type] = descriptor
        return self

    def validate(self) -> "Container":
        """
        Validate the container configuration.

        Checks for:
        - Missing dependencies
        - Circular dependencies
        - Lifetime mismatches (scoped depending on transient is ok,
          singleton depending on scoped is not)

        Raises ContainerError if validation fails.
        Returns self for chaining.
        """
        for service_type in self._descriptors:
            self._validate_service(service_type, set())
        return self

    def _validate_service(self, service_type: type, visited: set[type]) -> Lifetime:
        """Validate a service and return its effective lifetime."""
        if service_type in visited:
            raise CircularDependencyError(list(visited) + [service_type])

        descriptor = self._descriptors.get(service_type)
        if descriptor is None:
            raise MissingDependencyError(service_type)

        if descriptor.instance is not None:
            return descriptor.lifetime

        visited = visited | {service_type}

        target = descriptor.factory or descriptor.implementation
        if target is None:
            return descriptor.lifetime

        deps = self._get_dependencies(target)

        for deps_type in deps:
            if deps_type not in self._descriptors:
                raise MissingDependencyError(deps_type, service_type)

            dep_lifetime = self._validate_service(deps_type, visited)

            if (
                descriptor.lifetime == Lifetime.SINGLETON
                and dep_lifetime == Lifetime.SCOPED
            ):
                raise ContainerError(
                    f"Lifetime mismatch: singleton '{service_type.__name__}' "
                    f"cannot depend on scoped '{deps_type.__name__}'"
                )
        # validate decorators
        for decorator_type in descriptor.decorators:
            decorator_deps = self._get_dependencies(decorator_type)
            decorator_deps = [d for d in decorator_deps if d != service_type]

            for dep_type in decorator_deps:
                if dep_type not in self._descriptors:
                    raise MissingDependencyError(dep_type, decorator_type)
                self._validate_service(dep_type, visited)

        return descriptor.lifetime

    def _get_dependencies(self, target: Callable[..., Any]) -> list[type[Any]]:
        """Extract dependency types from a callable's type hints."""
        init = cast(Any, target).__init__ if isinstance(target, type) else target

        try:
            hints = get_type_hints(init)
        except Exception:
            # Some edge cases fail with get_type_hints
            return []

        hints.pop("return", None)

        deps = []
        for name, hint in hints.items():
            if name != "self":
                # Only include types we know about (registered services)
                # Skip primitives, Optional, etc.
                if isinstance(hint, type):
                    deps.append(hint)

        return deps

    # ─────────────────────────────────────────────────────────────────
    # Resolution
    # ─────────────────────────────────────────────────────────────────

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service.

        Raises MissingDependencyError if not registered.
        Raises CircularDependencyError if circular dependencies detected.
        """
        return self._resolve(service_type, {}, set())

    def resolve_optional(self, service_type: type[T]) -> T | None:
        """Resolve a service or return None if not registered."""
        try:
            return self.resolve(service_type)
        except MissingDependencyError:
            return None

    def scope(self) -> Scope:
        """Create a new scope for resolving scoped services."""
        return Scope(self)

    def _resolve(
        self,
        service_type: type[T],
        scoped_cache: dict[type, object],
        resolution_chain: set[type],
    ) -> T:
        # Circular dependency check
        if service_type in resolution_chain:
            raise CircularDependencyError(list(resolution_chain) + [service_type])

        descriptor = self._descriptors.get(service_type)
        if descriptor is None:
            raise MissingDependencyError(service_type)

        # Check caches (before decoration - we cache the final decorated instance)
        match descriptor.lifetime:
            case Lifetime.SINGLETON if service_type in self._singletons:
                return cast(T, self._singletons[service_type])
            case Lifetime.SCOPED if service_type in scoped_cache:
                return cast(T, scoped_cache[service_type])

        resolution_chain = resolution_chain | {service_type}

        # Create base instance
        instance = self._create(descriptor, scoped_cache, resolution_chain)

        # Apply decorators (in order: first decorator wraps the base)
        for decorator_type in descriptor.decorators:
            instance = self._create_decorator(
                decorator_type, service_type, instance, scoped_cache, resolution_chain
            )

        # Cache the final decorated instance
        match descriptor.lifetime:
            case Lifetime.SINGLETON:
                self._singletons[service_type] = instance
            case Lifetime.SCOPED:
                scoped_cache[service_type] = instance

        return cast(T, instance)

    def _create(
        self,
        descriptor: _ServiceDescriptor,
        scoped_cache: dict[type, object],
        resolution_chain: set[type],
    ) -> object:
        if descriptor.instance is not None:
            return descriptor.instance

        target = descriptor.factory or descriptor.implementation
        if target is None:
            raise ContainerError(
                f"No implementation for '{descriptor.service_type.__name__}'"
            )

        return self._inject(target, scoped_cache, resolution_chain)

    def _create_decorator(
        self,
        decorator_type: type[Any],
        service_type: type[Any],
        inner_instance: object,
        scoped_cache: dict[type[Any], object],
        resolution_chain: set[type[Any]],
    ) -> object:
        """Create a decorator instance, injecting the inner instance."""
        init = cast(Any, decorator_type).__init__

        try:
            hints = get_type_hints(init)
        except Exception:
            hints = {}

        hints.pop("return", None)

        sig = inspect.signature(init)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            hint = hints.get(name)
            if hint is None:
                continue

            # If this parameter expects the decorated type, inject the inner instance
            if hint == service_type or (
                isinstance(hint, type) and issubclass(service_type, hint)
            ):
                kwargs[name] = inner_instance
            elif hint in self._descriptors:
                kwargs[name] = self._resolve(hint, scoped_cache, resolution_chain)

        return decorator_type(**kwargs)

    def _inject(
        self,
        target: Callable[..., Any],
        scoped_cache: dict[type[Any], object],
        resolution_chain: set[type[Any]],
    ) -> object:
        """Call target with dependencies injected based on type hints."""
        init = cast(Any, target).__init__ if isinstance(target, type) else target

        try:
            hints = get_type_hints(init)
        except Exception:
            hints = {}

        hints.pop("return", None)

        kwargs = {}
        for name, hint in hints.items():
            if name != "self" and hint in self._descriptors:
                kwargs[name] = self._resolve(hint, scoped_cache, resolution_chain)

        return target(**kwargs)
