from dependency.core.agrupation.module import Module as Module
from dependency.core.exceptions import ResolutionError as ResolutionError
from dependency.core.resolution.container import Container as Container
from pydantic import BaseModel

class PluginMeta(BaseModel):
    """Metadata for the plugin.
    """
    name: str
    version: str

class Plugin(Module):
    """Plugin class for creating reusable components.

    Attributes:
        meta (PluginMeta): Metadata for the plugin
        config (BaseModel): Configuration model for the plugin
    """
    meta: PluginMeta
    @classmethod
    def resolve_container(cls, container: Container) -> None:
        """Resolve the plugin configuration.

        Args:
            container (Container): The application container.

        Raises:
            ResolutionError: If the configuration is invalid.
        """
