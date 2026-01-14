import pytest
from dependency.core.agrupation import Plugin, PluginMeta, module
from dependency.core.declaration import Component, component, instance, providers
from dependency.core.resolution import Container, ResolutionStrategy

@module()
class TPlugin(Plugin):
    meta = PluginMeta(name="test_plugin", version="0.1.0")

class TInterface:
    initialized: bool = False

@component(
    module=TPlugin,
    interface=TInterface,
)
class TComponent(Component):
    pass

@instance(
    component=TComponent,
    provider=providers.Resource,
)
class TInstance(TInterface):
    def __enter__(self) -> 'TInstance':
        self.initialized = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None: # type: ignore
        self.initialized = False

def test_resource() -> None:
    container = Container()
    TPlugin.resolve_container(container)
    providers = list(TPlugin.resolve_providers())

    assert TInstance.initialized == False

    ResolutionStrategy.resolution(container, providers)
    component: TInterface = TComponent.provide()
    assert component.initialized == True

    # TODO: Esto no está funcionando correctamente
    #container.shutdown_resources()
    TComponent.injection.injectable.provider.shutdown() # type: ignore
    assert component.initialized == False
    assert providers == [TComponent.injection.injectable]
