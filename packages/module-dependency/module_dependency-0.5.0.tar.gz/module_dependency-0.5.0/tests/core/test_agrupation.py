from pydantic import BaseModel
from dependency.core.agrupation import Plugin, PluginMeta, module
from dependency.core.resolution import Container

class TPluginConfig(BaseModel):
    field1: str
    field2: int

@module()
class TPlugin(Plugin):
    meta = PluginMeta(name="test_plugin", version="0.1.0")
    config: TPluginConfig

def test_agrupation() -> None:
    container = Container.from_dict({
        "field1": "value",
        "field2": 100
    })

    TPlugin.resolve_container(container)
    assert TPlugin.config.field1 == "value" and TPlugin.config.field2 == 100
