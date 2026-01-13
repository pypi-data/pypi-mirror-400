from abc import ABC, abstractmethod
from typing import Union

from repen.components import Component


class Renderer(ABC):
    def __init__(self, **metadata) -> None:
        self.metadata = metadata

    @abstractmethod
    def render(self, title: str, root: Component) -> Union[str, bytes]:
        pass
