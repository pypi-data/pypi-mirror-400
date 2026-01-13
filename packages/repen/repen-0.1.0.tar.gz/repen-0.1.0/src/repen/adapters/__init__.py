from repen.adapters.base import ComponentAdapter
from repen.adapters.figure import (FigureFromTupleAdapter,
                                   MatplotlibFigureAdapter)
from repen.adapters.image import (BytesImageAdapter, PathImageAdapter,
                                  SVGImageAdapter)
from repen.adapters.metric import (MetricsFromDictAdapter,
                                   MetricsFromListAdapter)
from repen.adapters.registry import AdapterRegistry
from repen.adapters.table import PandasTableAdapter
from repen.adapters.text import TextAdapter

# Table
try:
    import pandas

    AdapterRegistry.register(PandasTableAdapter())
except:
    pass

# Metrics
AdapterRegistry.register(MetricsFromDictAdapter())
AdapterRegistry.register(MetricsFromListAdapter())

# Figure
AdapterRegistry.register(FigureFromTupleAdapter())

try:
    import matplotlib

    AdapterRegistry.register(MatplotlibFigureAdapter())
except:
    pass

# Image
AdapterRegistry.register(PathImageAdapter())
AdapterRegistry.register(BytesImageAdapter())
AdapterRegistry.register(SVGImageAdapter())

try:
    import PIL
    from repen.adapters.image import PillowImageAdapter

    AdapterRegistry.register(PillowImageAdapter())
except:
    pass

# Text
AdapterRegistry.register(TextAdapter())

__all__ = [
    "ComponentAdapter",
    "AdapterRegistry",
]
