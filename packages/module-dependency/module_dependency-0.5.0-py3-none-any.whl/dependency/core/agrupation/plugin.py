import logging
from pydantic import BaseModel
from typing import get_type_hints
from dependency.core.agrupation.module import Module
from dependency.core.resolution.container import Container
from dependency.core.exceptions import ResolutionError
_logger = logging.getLogger("dependency.loader")

class PluginMeta(BaseModel):
    """Metadata for the plugin.
    """
    name: str
    version: str

    def __str__(self) -> str:
        return f"Plugin {self.name} ({self.version})"

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
        try:
            cls.inject_container(container)
            config_cls = get_type_hints(cls).get("config", object)
            if issubclass(config_cls, BaseModel):
                setattr(cls, "config", config_cls(**container.config()))
            else:
                _logger.warning(f"Plugin {cls.meta} has no valid config class")
        except Exception as e:
            raise ResolutionError(f"Failed to resolve plugin config for {cls.meta}") from e
