from j2_ioc.errors.container_error import ContainerError


class MissingDependencyError(ContainerError):
    """Raised when a required dependency is not registered in the container."""

    def __init__(self, service_type: type, required_by: type | None = None):
        self.service_type = service_type
        self.required_by = required_by
        message = f"'{service_type.__name__}' is not registered"
        if required_by:
            message += f", required by {required_by.__name__}"
        super().__init__(message)
