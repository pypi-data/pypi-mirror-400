from j2_ioc.errors.container_error import ContainerError


class CircularDependencyError(ContainerError):
    """Raised when a circular dependency is detected in the container."""

    def __init__(self, chain: list[type]):
        self.chain = chain
        cycle = " -> ".join(t.__name__ for t in chain)
        super().__init__(f"Circular dependency detected: {cycle}")
