from typing import Dict, List, Type, Union

from repen.components import (Component, Composite, Figure, Image, Metric,
                              MetricsGroup, Table, TableHeader, TableRow, Text,
                              TextBlock, TextLines, TextSpan, VStack)
from repen.renderers.base import Renderer
from repen.renderers.html.datatable import JS_DATA_TABLE, JS_JQUERY
from repen.renderers.html.processor import (HTMLComponentProcessor,
                                            HTMLCompositeProcessor)
from repen.renderers.html.processor_figure import HTMLFigureProcessor
from repen.renderers.html.processor_image import HTMLImageProcessor
from repen.renderers.html.processor_layout import HTMLVStackProcessor
from repen.renderers.html.processor_metric import (HTMLMetricProcessor,
                                                   HTMLMetricsGroupProcessor)
from repen.renderers.html.processor_table import (HTMLTableHeaderProcessor,
                                                  HTMLTableProcessor,
                                                  HTMLTableRowProcessor)
from repen.renderers.html.processor_text import (HTMLTextBlockProcessor,
                                                 HTMLTextLinesProcessor,
                                                 HTMLTextProcessor,
                                                 HTMLTextSpanProcessor)
from repen.renderers.html.theme_registry import HTMLThemeRegistry


class HTMLRenderer(Renderer):
    def __init__(self, **metadata) -> None:
        super().__init__(**metadata)
        self._theme: str = metadata.get("theme", "default")
        self._theme_registry = HTMLThemeRegistry()
        self._output: List[str] = []
        self._component_processors: Dict[Type, HTMLComponentProcessor] = {
            Text: HTMLTextProcessor(),
            Image: HTMLImageProcessor(),
            Metric: HTMLMetricProcessor(),
        }
        self._composite_processors: Dict[Type, HTMLCompositeProcessor] = {
            # Text
            TextBlock: HTMLTextBlockProcessor(),
            TextSpan: HTMLTextSpanProcessor(),
            TextLines: HTMLTextLinesProcessor(),
            # Layout
            VStack: HTMLVStackProcessor(),
            # Figure
            Figure: HTMLFigureProcessor(),
            # Metrics
            MetricsGroup: HTMLMetricsGroupProcessor(),
            # Table
            Table: HTMLTableProcessor(),
            TableHeader: HTMLTableHeaderProcessor(),
            TableRow: HTMLTableRowProcessor(),
        }

    def render(self, title: str, root: Component) -> Union[str, bytes]:
        self.begin(title)
        self.component(root)
        self.end()
        return self.output()

    def begin(self, title: str = "") -> None:
        self._output.append(
            f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>{self._theme_registry.css(self._theme)}</style>
    <script>
        {JS_JQUERY}
        {JS_DATA_TABLE}
    </script>
</head>
<body>
"""
        )

    def end(self) -> None:
        self._output.append(
            """
       <script>
            $("table").dataTable();
       </script>
   </body>
</html>
"""
        )

    def component(self, component: Component) -> None:
        if isinstance(component, Composite):
            processor = self._composite_processors.get(
                type(component),
                HTMLCompositeProcessor(),
            )
            composite_begin = processor.begin(component)
            if composite_begin is not None:
                self._output.append(composite_begin)

            for child in component.children:
                composite_begin_component = processor.begin_child(component, child)
                if composite_begin_component is not None:
                    self._output.append(composite_begin_component)

                self.component(child)

                composite_end_component = processor.end_child(component, child)
                if composite_end_component is not None:
                    self._output.append(composite_end_component)

            composite_end = processor.end(component)
            if composite_end is not None:
                self._output.append(composite_end)
        else:
            processor = self._component_processors.get(
                type(component),
                HTMLComponentProcessor(),
            )
            component_processed = processor.process(component)
            if component_processed:
                self._output.append(component_processed)

    def output(self) -> Union[str, bytes]:
        return "".join(self._output)
