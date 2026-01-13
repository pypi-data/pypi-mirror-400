from typing import Optional

from repen.components import Component, Composite, TextLike
from repen.renderers.html.processor import HTMLCompositeProcessor


class HTMLFigureProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        return "<figure>"

    def begin_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "<figcaption>" if isinstance(component, TextLike) else None

    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "</figcaption>" if isinstance(component, TextLike) else None

    def end(self, composite: Composite) -> Optional[str]:
        return "</figure>"
