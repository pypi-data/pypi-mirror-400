from typing import Any, cast

from repen.adapters.base import ComponentAdapter
from repen.adapters.registry import AdapterRegistry
from repen.components import Component, Table, TableHeader, TableRow


class PandasTableAdapter(ComponentAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        try:
            import pandas as pd

            return isinstance(raw_data, pd.DataFrame)
        except ImportError:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        import pandas as pd

        df = cast(pd.DataFrame, raw_data)
        table = Table(**metadata)

        header = TableHeader(**metadata)
        for col in df.columns:
            cell_component = AdapterRegistry.create(str(col), **metadata)
            header.add(cell_component)
        table.add(header)

        for _, row in df.iterrows():
            table_row = TableRow(**metadata)
            for value in row:
                cell_component = AdapterRegistry.create(str(value), **metadata)
                table_row.add(cell_component)
            table.add(table_row)

        return table
