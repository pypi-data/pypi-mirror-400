from typing import Any

from repen.components.base import Composite


class Figure(Composite):
    def __init__(self, **metadata: Any) -> None:
        super().__init__(**metadata)
