from abc import ABC, abstractmethod
from dependency_injector import containers, providers
from dependency.core.agrupation import Module, module
from dependency.core.declaration import Component, component, instance

class TInterface(ABC):
    @abstractmethod
    def method(self) -> str:
        pass

@module()
class TModule(Module):
    pass

@component(
    module=TModule,
    interface=TInterface,
)
class TComponent(Component):
    pass

@instance(
    component=TComponent,
    imports=[],
    provider=providers.Singleton,
)
class TInstance(TInterface):
    def method(self) -> str:
        return "Hello, World!"

def test_declaration() -> None:
    container = containers.DynamicContainer()
    setattr(container, TModule.injection.name, TModule.injection.inject_cls())
    for provider in TModule.injection.resolve_providers():
        provider.do_injection()

    assert TModule.__name__ == "TModule"
    assert TComponent.interface_cls.__name__ == "TInterface"
    assert TInstance.__name__ == "TInstance"

    component: TInterface = TComponent.provide()
    assert isinstance(component, TInterface)
    assert component.method() == "Hello, World!"
