from typing import List, Union

from repen.components import Component, Composite
from repen.renderers.base import Renderer


class DebugRenderer(Renderer):
    def __init__(self, **metadata) -> None:
        super().__init__(**metadata)

    def render(self, title: str, root: Component) -> Union[str, bytes]:
        result = []
        result.append(f"{'=' * 60}")
        result.append("DEBUG RENDERER")
        result.append(f"{'=' * 60}")
        result.append(f"TITLE: {title}")
        result.append("TREE:")
        result.append("")

        self._render_component(root, 0, result)

        result.append("")
        result.append(f"{'=' * 60}")

        return "\n".join(result)

    def _render_component(
        self,
        component: Component,
        depth: int,
        result: List[str],
        prefix: str = "",
        is_last: bool = True,
    ) -> None:
        connector = "└── " if is_last else "├── "
        result.append(f"{prefix}{connector}{component}")

        if isinstance(component, Composite):
            children = component.children
            for idx, child in enumerate(children):
                is_last_child = idx == len(children) - 1
                if is_last:
                    child_prefix = prefix + "    "
                else:
                    child_prefix = prefix + "│   "
                self._render_component(
                    child, depth + 1, result, child_prefix, is_last_child
                )
