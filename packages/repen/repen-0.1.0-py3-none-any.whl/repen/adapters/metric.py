from typing import Any, Dict, List, Tuple, cast

from repen.adapters.base import ComponentAdapter
from repen.components import Component, Metric, MetricsGroup, MetricVariant


class MetricsAdapter(ComponentAdapter):
    def __init__(self) -> None:
        super().__init__(1)

    def _parse_variant(self, variant: Any) -> MetricVariant:
        if isinstance(variant, MetricVariant):
            return variant

        if isinstance(variant, str):
            try:
                return MetricVariant(variant)
            except ValueError:
                variant_lower = variant.lower()
                for enum_member in MetricVariant:
                    if enum_member.value == variant_lower:
                        return enum_member
                for enum_member in MetricVariant:
                    if enum_member.name.lower() == variant_lower:
                        return enum_member

        raise ValueError(
            f"Invalid variant: {variant}. Must be one of: {[v.value for v in MetricVariant]}"
        )

    def _parse_metric_data(self, label: str, data: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {"label": label}
        if isinstance(data, Dict):
            result["value"] = data.get("value", None)
            result["unit"] = data.get("unit", None)
            result["variant"] = data.get("variant", "default")
            result["precision"] = data.get("precision", None)
        elif isinstance(data, Tuple):
            length = len(data)
            if length >= 1:
                result["value"] = data[0]
            if length >= 2 and data[1] is not None:
                result["unit"] = data[1]
            if length >= 3 and data[2] is not None:
                result["variant"] = data[2]
            if length >= 4 and data[3] is not None:
                result["precision"] = data[3]
        else:
            result["value"] = data

        return result

    def _validate_metric_data(self, data: Dict[str, Any]) -> bool:
        try:
            value = data.get("value")
            if value is None or not isinstance(value, (str, int, float)):
                return False

            unit = data.get("unit", None)
            if unit is not None and not isinstance(unit, str):
                return False

            variant = data.get("variant", "default")
            self._parse_variant(variant)

            precision = data.get("precision", None)
            if precision is not None:
                if not isinstance(precision, int) or precision < 0:
                    return False

            return True
        except:
            return False


class MetricsFromDictAdapter(MetricsAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if not isinstance(raw_data, Dict):
            return False

        try:
            for label, value in raw_data.items():
                if not isinstance(label, str):
                    return False

                metric_data = self._parse_metric_data(label, value)
                if not self._validate_metric_data(metric_data):
                    return False

            return True
        except:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        raw_data_dict = cast(Dict, raw_data)

        group = MetricsGroup(**metadata)
        for label, value in raw_data_dict.items():
            metric_data = self._parse_metric_data(label, value)
            metric = Metric(
                label=metric_data["label"],
                value=metric_data["value"],
                unit=metric_data.get("unit"),
                variant=self._parse_variant(metric_data.get("variant", "default")),
                precision=metric_data.get("precision"),
                **metadata,
            )
            group.add(metric)

        return group


class MetricsFromListAdapter(MetricsAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if not isinstance(raw_data, List):
            return False

        try:
            for item in raw_data:
                if isinstance(item, Tuple):
                    if len(item) < 2:
                        return False

                    label = item[0]
                    if not isinstance(label, str):
                        return False

                    metric_data = self._parse_metric_data(label, item[1:])
                elif isinstance(item, Dict):
                    if "label" not in item or "value" not in item:
                        return False

                    label = item["label"]
                    if not isinstance(label, str):
                        return False

                    metric_data = self._parse_metric_data(label, item)
                else:
                    return False

                if not self._validate_metric_data(metric_data):
                    return False
            return True
        except:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        raw_data_list = cast(List, raw_data)

        group = MetricsGroup(**metadata)
        for item in raw_data_list:
            if isinstance(item, Tuple):
                label = item[0]
                metric_data = self._parse_metric_data(label, item[1:])
            elif isinstance(item, Dict):
                label = item["label"]
                metric_data = self._parse_metric_data(label, item)
            else:
                continue

            metric = Metric(
                label=metric_data["label"],
                value=metric_data["value"],
                unit=metric_data.get("unit"),
                variant=self._parse_variant(metric_data.get("variant", "default")),
                precision=metric_data.get("precision"),
                **metadata,
            )
            group.add(metric)

        return group
