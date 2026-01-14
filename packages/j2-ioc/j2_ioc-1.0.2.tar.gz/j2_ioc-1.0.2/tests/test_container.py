"""Tests for the Container class."""

import pytest
from abc import ABC, abstractmethod
from python_ioc import Container, Lifetime
from python_ioc.errors import (
    CircularDependencyError,
    ContainerError,
    MissingDependencyError,
)


# Module-level classes for circular dependency test
class CircularServiceA:
    def __init__(self, b: "CircularServiceB"):
        self.b = b


class CircularServiceB:
    def __init__(self, a: CircularServiceA):
        self.a = a


class TestBasicRegistration:
    """Test basic service registration."""

    def test_container_initialization(self) -> None:
        """Test that a container can be initialized."""
        container = Container()
        assert container is not None

    def test_transient_registration(self) -> None:
        """Test registering a transient service."""

        class Service:
            pass

        container = Container().transient(Service)

        instance1 = container.resolve(Service)
        instance2 = container.resolve(Service)

        assert instance1 is not instance2

    def test_singleton_registration(self) -> None:
        """Test registering a singleton service."""

        class Service:
            pass

        container = Container().singleton(Service)

        instance1 = container.resolve(Service)
        instance2 = container.resolve(Service)

        assert instance1 is instance2

    def test_scoped_registration(self) -> None:
        """Test registering a scoped service."""

        class Service:
            pass

        container = Container().scoped(Service)

        with container.scope() as scope1:
            instance1 = scope1.resolve(Service)
            instance2 = scope1.resolve(Service)
            assert instance1 is instance2

        with container.scope() as scope2:
            instance3 = scope2.resolve(Service)
            assert instance1 is not instance3

    def test_instance_registration(self) -> None:
        """Test registering an existing instance."""

        class Service:
            def __init__(self, value: str):
                self.value = value

        instance = Service("test")
        container = Container().instance(Service, instance)

        resolved = container.resolve(Service)
        assert resolved is instance
        assert resolved.value == "test"


class TestAbstractBaseClasses:
    """Test registration with ABCs."""

    def test_abc_with_implementation(self) -> None:
        """Test registering an ABC with a concrete implementation."""

        class Repository(ABC):
            @abstractmethod
            def get(self, id: int) -> dict: ...

        class ConcreteRepository(Repository):
            def get(self, id: int) -> dict:
                return {"id": id}

        container = Container().singleton(Repository, ConcreteRepository)

        repo = container.resolve(Repository)
        assert isinstance(repo, ConcreteRepository)
        assert repo.get(1) == {"id": 1}


class TestDependencyInjection:
    """Test constructor dependency injection."""

    def test_simple_dependency_injection(self) -> None:
        """Test injecting a single dependency."""

        class Database:
            def query(self) -> str:
                return "result"

        class Service:
            def __init__(self, db: Database):
                self.db = db

        container = Container().singleton(Database).transient(Service)

        service = container.resolve(Service)
        assert isinstance(service.db, Database)
        assert service.db.query() == "result"

    def test_multiple_dependencies(self) -> None:
        """Test injecting multiple dependencies."""

        class Logger:
            def log(self, msg: str) -> str:
                return f"LOG: {msg}"

        class Database:
            pass

        class Service:
            def __init__(self, db: Database, logger: Logger):
                self.db = db
                self.logger = logger

        container = Container().singleton(Database).singleton(Logger).transient(Service)

        service = container.resolve(Service)
        assert isinstance(service.db, Database)
        assert isinstance(service.logger, Logger)
        assert service.logger.log("test") == "LOG: test"

    def test_nested_dependencies(self) -> None:
        """Test resolving nested dependencies."""

        class Config:
            def get(self, key: str) -> str:
                return "value"

        class Database:
            def __init__(self, config: Config):
                self.config = config

        class Service:
            def __init__(self, db: Database):
                self.db = db

        container = Container().singleton(Config).singleton(Database).transient(Service)

        service = container.resolve(Service)
        assert isinstance(service.db, Database)
        assert isinstance(service.db.config, Config)
        assert service.db.config.get("key") == "value"


class TestFactoryRegistration:
    """Test factory function registration."""

    def test_factory_function(self) -> None:
        """Test registering a factory function."""

        class Config:
            def __init__(self, value: str):
                self.value = value

        def create_config() -> Config:
            return Config("test")

        container = Container().factory(Config, create_config)

        config = container.resolve(Config)
        assert isinstance(config, Config)
        assert config.value == "test"

    def test_factory_with_dependencies(self) -> None:
        """Test factory function with injected dependencies."""

        class Config:
            def __init__(self):
                self.db_url = "postgresql://localhost/db"

        class Connection:
            def __init__(self, url: str):
                self.url = url

        def create_connection(config: Config) -> Connection:
            return Connection(config.db_url)

        container = (
            Container()
            .singleton(Config)
            .factory(Connection, create_connection, Lifetime.SINGLETON)
        )

        conn = container.resolve(Connection)
        assert isinstance(conn, Connection)
        assert conn.url == "postgresql://localhost/db"

    def test_factory_lifetime(self) -> None:
        """Test factory function respects lifetime."""
        call_count = 0

        class Service:
            pass

        def create_service() -> Service:
            nonlocal call_count
            call_count += 1
            return Service()

        # Transient factory
        container = Container().factory(Service, create_service, Lifetime.TRANSIENT)
        container.resolve(Service)
        container.resolve(Service)
        assert call_count == 2

        # Singleton factory
        call_count = 0
        container = Container().factory(Service, create_service, Lifetime.SINGLETON)
        container.resolve(Service)
        container.resolve(Service)
        assert call_count == 1


class TestDecorators:
    """Test decorator pattern support."""

    def test_simple_decorator(self) -> None:
        """Test applying a decorator to a service."""

        class Repository(ABC):
            @abstractmethod
            def get(self, id: int) -> dict: ...

        class ConcreteRepository(Repository):
            def get(self, id: int) -> dict:
                return {"id": id, "cached": False}

        class CachedRepository(Repository):
            def __init__(self, inner: Repository):
                self.inner = inner
                self.cache = {}

            def get(self, id: int) -> dict:
                if id not in self.cache:
                    result = self.inner.get(id)
                    result["cached"] = True
                    self.cache[id] = result
                return self.cache[id]

        container = (
            Container()
            .singleton(Repository, ConcreteRepository)
            .decorate(Repository, CachedRepository)
        )

        repo = container.resolve(Repository)
        assert isinstance(repo, CachedRepository)
        result1 = repo.get(1)
        result2 = repo.get(1)
        assert result1 is result2
        assert result1["cached"] is True

    def test_decorator_with_additional_dependencies(self) -> None:
        """Test decorator with its own dependencies."""

        class Cache:
            def __init__(self):
                self.store = {}

        class Repository(ABC):
            @abstractmethod
            def get(self, id: int) -> str: ...

        class ConcreteRepository(Repository):
            def get(self, id: int) -> str:
                return f"data-{id}"

        class CachedRepository(Repository):
            def __init__(self, inner: Repository, cache: Cache):
                self.inner = inner
                self.cache = cache

            def get(self, id: int) -> str:
                if id not in self.cache.store:
                    self.cache.store[id] = self.inner.get(id)
                return self.cache.store[id]

        container = (
            Container()
            .singleton(Cache)
            .singleton(Repository, ConcreteRepository)
            .decorate(Repository, CachedRepository)
        )

        repo = container.resolve(Repository)
        assert repo.get(1) == "data-1"
        assert repo.get(1) == "data-1"

    def test_multiple_decorators(self) -> None:
        """Test applying multiple decorators."""

        class Service(ABC):
            @abstractmethod
            def execute(self) -> str: ...

        class ConcreteService(Service):
            def execute(self) -> str:
                return "base"

        class Decorator1(Service):
            def __init__(self, inner: Service):
                self.inner = inner

            def execute(self) -> str:
                return f"[D1:{self.inner.execute()}]"

        class Decorator2(Service):
            def __init__(self, inner: Service):
                self.inner = inner

            def execute(self) -> str:
                return f"[D2:{self.inner.execute()}]"

        container = (
            Container()
            .singleton(Service, ConcreteService)
            .decorate(Service, Decorator1)
            .decorate(Service, Decorator2)
        )

        service = container.resolve(Service)
        # Decorators applied in order: D2(D1(base))
        assert service.execute() == "[D2:[D1:base]]"


class TestValidation:
    """Test container validation."""

    def test_validation_success(self) -> None:
        """Test validation passes for valid configuration."""

        class Database:
            pass

        class Service:
            def __init__(self, db: Database):
                self.db = db

        container = Container().singleton(Database).transient(Service)

        # Should not raise
        container.validate()

    def test_missing_dependency_error(self) -> None:
        """Test validation detects missing dependencies."""

        class UnregisteredService:
            pass

        class Service:
            def __init__(self, dep: UnregisteredService):
                self.dep = dep

        container = Container().transient(Service)

        with pytest.raises(MissingDependencyError) as exc_info:
            container.validate()

        assert "UnregisteredService" in str(exc_info.value)

    def test_circular_dependency_error(self) -> None:
        """Test validation detects circular dependencies."""
        container = Container().transient(CircularServiceA).transient(CircularServiceB)

        # Circular dependencies are detected during validation
        with pytest.raises(CircularDependencyError) as exc_info:
            container.validate()

        assert "CircularService" in str(exc_info.value)

    def test_lifetime_mismatch_error(self) -> None:
        """Test validation detects lifetime mismatches."""

        class ScopedService:
            pass

        class SingletonService:
            def __init__(self, scoped: ScopedService):
                self.scoped = scoped

        container = Container().scoped(ScopedService).singleton(SingletonService)

        with pytest.raises(ContainerError) as exc_info:
            container.validate()

        assert "Lifetime mismatch" in str(exc_info.value)
        assert "SingletonService" in str(exc_info.value)
        assert "ScopedService" in str(exc_info.value)


class TestScope:
    """Test scope functionality."""

    def test_scope_isolation(self) -> None:
        """Test that scopes are isolated from each other."""

        class Service:
            pass

        container = Container().scoped(Service)

        with container.scope() as scope1:
            service1 = scope1.resolve(Service)

        with container.scope() as scope2:
            service2 = scope2.resolve(Service)

        assert service1 is not service2

    def test_scope_reuse_within_scope(self) -> None:
        """Test that scoped services are reused within the same scope."""

        class Service:
            pass

        container = Container().scoped(Service)

        with container.scope() as scope:
            service1 = scope.resolve(Service)
            service2 = scope.resolve(Service)
            assert service1 is service2

    def test_singleton_shared_across_scopes(self) -> None:
        """Test that singletons are shared across scopes."""

        class Service:
            pass

        container = Container().singleton(Service)

        with container.scope() as scope1:
            service1 = scope1.resolve(Service)

        with container.scope() as scope2:
            service2 = scope2.resolve(Service)

        assert service1 is service2

    def test_resolve_optional(self) -> None:
        """Test resolve_optional returns None for unregistered services."""

        class Service:
            pass

        container = Container()

        with container.scope() as scope:
            service = scope.resolve_optional(Service)
            assert service is None

    def test_resolve_optional_returns_service(self) -> None:
        """Test resolve_optional returns service if registered."""

        class Service:
            pass

        container = Container().singleton(Service)

        with container.scope() as scope:
            service = scope.resolve_optional(Service)
            assert service is not None
            assert isinstance(service, Service)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_resolve_unregistered_service(self) -> None:
        """Test resolving unregistered service raises error."""

        class Service:
            pass

        container = Container()

        with pytest.raises(MissingDependencyError):
            container.resolve(Service)

    def test_service_with_no_dependencies(self) -> None:
        """Test service with no constructor dependencies."""

        class Service:
            def __init__(self):
                self.value = "test"

        container = Container().singleton(Service)

        service = container.resolve(Service)
        assert service.value == "test"

    def test_chaining_registrations(self) -> None:
        """Test chaining multiple registrations."""

        class ServiceA:
            pass

        class ServiceB:
            pass

        class ServiceC:
            pass

        container = Container().singleton(ServiceA).scoped(ServiceB).transient(ServiceC)

        a = container.resolve(ServiceA)
        with container.scope() as scope:
            b = scope.resolve(ServiceB)
            c = scope.resolve(ServiceC)

        assert isinstance(a, ServiceA)
        assert isinstance(b, ServiceB)
        assert isinstance(c, ServiceC)

    def test_decorate_unregistered_service_raises_error(self) -> None:
        """Test decorating an unregistered service raises error."""

        class Service(ABC):
            pass

        class Decorator(Service):
            def __init__(self, inner: Service):
                self.inner = inner

        container = Container()

        with pytest.raises(Exception):  # Should raise ConnectionError based on code
            container.decorate(Service, Decorator)
