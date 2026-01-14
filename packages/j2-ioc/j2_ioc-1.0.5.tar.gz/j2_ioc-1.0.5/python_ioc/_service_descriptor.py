from dataclasses import field, dataclass
from collections.abc import Callable
from python_ioc.lifetime import Lifetime


@dataclass
class _ServiceDescriptor:
    service_type: type
    implementation: type | None = None
    factory: Callable | None = None
    lifetime: Lifetime = Lifetime.TRANSIENT
    instance: object | None = None
    decorators: list[type] = field(default_factory=list)
