"""Container dependency for FastAPI."""

from intelliclaim.application.container import Container

_container: Container | None = None


def set_container(container: Container) -> None:
    """Set the global application container."""
    global _container
    _container = container


def get_container() -> Container:
    """Retrieve the application container."""
    if _container is None:
        msg = "Application container not initialized"
        raise RuntimeError(msg)
    return _container
