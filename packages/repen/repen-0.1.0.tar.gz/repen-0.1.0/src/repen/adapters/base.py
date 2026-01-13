from abc import ABC, abstractmethod
from typing import Any

from repen.components import Component


class ComponentAdapter(ABC):
    def __init__(self, priority: int = 0) -> None:
        self.priority = priority

    @abstractmethod
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        pass

    @abstractmethod
    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        pass
