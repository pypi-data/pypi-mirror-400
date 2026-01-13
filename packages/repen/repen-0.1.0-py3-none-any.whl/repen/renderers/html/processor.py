from typing import Optional

from repen.components import Component, Composite


class HTMLComponentProcessor:
    def process(self, component: Component) -> Optional[str]:
        return None


class HTMLCompositeProcessor:
    def begin(self, composite: Composite) -> Optional[str]:
        return None

    def begin_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return None

    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return None

    def end(self, composite: Composite) -> Optional[str]:
        return None
