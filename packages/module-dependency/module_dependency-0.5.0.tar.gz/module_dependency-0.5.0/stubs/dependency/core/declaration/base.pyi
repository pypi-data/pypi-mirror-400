from abc import ABC

class ABCComponent(ABC):
    """Abstract base class for all components.
    """
    interface_cls: type
