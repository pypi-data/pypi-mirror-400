from enum import Enum
from typing import Optional, Union, cast

from repen.components.base import Component, Composite, Spacing


class MetricVariant(Enum):
    DEFAULT = "default"
    HIGHLIGHT = "highlight"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class Metric(Component):
    def __init__(
        self,
        label: str,
        value: Union[str, int, float],
        unit: Optional[str] = None,
        variant: MetricVariant = MetricVariant.DEFAULT,
        precision: Optional[int] = None,
        **metadata,
    ) -> None:
        super().__init__(**metadata)
        self.label = label
        self.value = value
        self.unit = unit
        self.variant = variant
        self.precision = precision

        if isinstance(value, (int, float)) and precision is not None:
            self.formatted_value = f"{value:.{precision}f}"
        else:
            self.formatted_value = str(value)

    def copy(self) -> Component:
        return Metric(
            self.label,
            self.value,
            self.unit,
            self.variant,
            self.precision,
            **self.metadata,
        )

    def __repr__(self) -> str:
        unit = f", unit='{self.unit}'" if self.unit is not None else ""
        precision = (
            f", precision={self.precision}" if self.precision is not None else ""
        )
        return f"{self.__class__.__name__} (label='{self.label}', value={self.formatted_value}, variant={self.variant.value}{unit}{precision})"


class MetricsGroup(Composite):
    def __init__(self, spacing: Spacing = Spacing.XS, **metadata):
        super().__init__(**metadata)
        self.spacing = spacing

    def copy(self) -> Component:
        new_instance = cast(MetricsGroup, super().copy())
        new_instance.spacing = self.spacing
        return new_instance

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} (spacing={self.spacing})"
