from typing import Optional, cast

from repen.components import Component, Composite, Metric, MetricsGroup
from repen.renderers.html.processor import (HTMLComponentProcessor,
                                            HTMLCompositeProcessor)


class HTMLMetricProcessor(HTMLComponentProcessor):
    def process(self, component: Component) -> Optional[str]:
        metric = cast(Metric, component)
        classes = f"metric {metric.variant.value}"

        return f"""
<div class="{classes}">
    <div class="label">{metric.label}</div>
    <div class="value">
        {metric.formatted_value}
        {f'<span class="unit">{metric.unit}</span>' if metric.unit else ''}
    </div>
</div>
        """


class HTMLMetricsGroupProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        group = cast(MetricsGroup, composite)
        style = f"--spacing: var(--spacing-{group.spacing.value});"
        return f'<div class="metrics-group" style="{style}">'

    def end(self, composite: Composite) -> Optional[str]:
        return "</div>"
