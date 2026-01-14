from dependency.core.agrupation.plugin import Plugin as Plugin
from dependency.core.injection.injectable import Injectable as Injectable
from dependency.core.resolution.container import Container as Container
from dependency.core.resolution.resolver import InjectionResolver as InjectionResolver
from typing import Iterable

class Entrypoint:
    """Entrypoint for the application.

    Attributes:
        init_time (float): Time when the entrypoint was initialized.
    """
    init_time: float
    resolver: InjectionResolver
    def __init__(self, container: Container, plugins: Iterable[type[Plugin]]) -> None: ...
    def main_loop(self) -> None:
        """Main loop for the application. Waits indefinitely."""
