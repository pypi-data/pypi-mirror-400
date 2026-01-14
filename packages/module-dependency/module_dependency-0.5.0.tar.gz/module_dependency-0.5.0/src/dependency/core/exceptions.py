
class DependencyError(Exception):
    """Base class for all dependency-related errors."""

class DeclarationError(DependencyError):
    """Exception raised for errors in the declaration of dependencies."""
class ResolutionError(DependencyError):
    """Exception raised for errors during the resolution of dependencies."""
class InitializationError(DependencyError):
    """Exception raised for errors during the initialization of components."""


class CancelInitialization(DependencyError):
    """Exception to cancel the initialization of a component."""
