import base64
import io
from typing import Any, List, Tuple, cast

from repen.adapters.base import ComponentAdapter
from repen.adapters.registry import AdapterRegistry
from repen.components import Component, Figure, Image, ImageFormat, TextLike

DEFAULT_DPI = 1200


class MatplotlibFigureAdapter(ComponentAdapter):
    def __init__(self) -> None:
        super().__init__(2)

    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        from matplotlib.figure import Figure as MPLFigure

        return isinstance(raw_data, MPLFigure)

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        image_format = metadata.pop("format", "svg")
        if image_format == "svg":
            image = self._to_svg(raw_data, **metadata)
        elif image_format == "png":
            image = self._to_png(raw_data, **metadata)
        else:
            raise ValueError(f"Unsupported format: {image_format}")

        figure = Figure(**metadata)
        figure.add(image)
        return figure

    def _to_svg(self, raw_data: Any, **metadata: Any) -> Image:
        from matplotlib.figure import Figure as MPLFigure

        output = io.StringIO()
        dpi = metadata.get("dpi", DEFAULT_DPI)
        figure = cast(MPLFigure, raw_data)
        figure.savefig(output, format="svg", dpi=dpi, bbox_inches="tight")

        image_data = output.getvalue()
        output.close()

        return Image(image_data, ImageFormat.SVG)

    def _to_png(self, raw_data: Any, **metadata: Any) -> Image:
        from matplotlib.figure import Figure as MPLFigure

        output = io.BytesIO()
        dpi = metadata.get("dpi", DEFAULT_DPI)
        figure = cast(MPLFigure, raw_data)
        figure.savefig(output, format="png", dpi=dpi, bbox_inches="tight")

        image_data = base64.b64encode(output.getvalue()).decode()
        output.close()

        return Image(image_data, ImageFormat.PNG)


class FigureFromTupleAdapter(ComponentAdapter):
    def __init__(self) -> None:
        super().__init__(3)

    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if isinstance(raw_data, Tuple):
            if len(raw_data) != 2:
                return False

            has_figure_or_image = False
            has_caption = False
            for component_data in raw_data:
                component = AdapterRegistry.create(component_data, **metadata)
                if isinstance(component, (Figure, Image)):
                    has_figure_or_image = True

                if isinstance(component, TextLike):
                    has_caption = True

            return has_figure_or_image and has_caption
        return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        raw_tuple = cast(Tuple, raw_data)
        figure = Figure()

        components: List[Component] = []
        for component_data in raw_tuple:
            component = AdapterRegistry.create(component_data, **metadata)
            if isinstance(component, Figure):
                figure = component
            else:
                components.append(component)

        figure.add_all(*components)
        return figure
