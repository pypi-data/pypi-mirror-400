from typing import Optional

from repen.components import Component, Composite
from repen.renderers.html.processor import HTMLCompositeProcessor


class HTMLTableHeaderProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        return "<thead><tr>"

    def begin_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "<th>"

    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "</th>"

    def end(self, composite: Composite) -> Optional[str]:
        return "</tr></thead>"


class HTMLTableRowProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        return "<tr>"

    def begin_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "<td>"

    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "</td>"

    def end(self, composite: Composite) -> Optional[str]:
        return "</tr>"


class HTMLTableProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        return "<table>"

    def end(self, composite: Composite) -> Optional[str]:
        return "</table>"
