from typing import Optional, cast

from repen.components import Component, Composite, VStack
from repen.renderers.html.processor import HTMLCompositeProcessor


class HTMLVStackProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        vstack = cast(VStack, composite)
        style = f"style='--spacing: var(--spacing-{vstack.spacing.value})'"
        return f"<div class='layout vstack' {style}>"

    def begin_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return f"<div class='item'>"

    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "</div>"

    def end(self, composite: Composite) -> Optional[str]:
        return "</div>"
