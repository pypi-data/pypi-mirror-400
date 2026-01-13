from typing import Optional, cast

from repen.components import Component, Image, ImageFormat
from repen.renderers.html.processor import HTMLComponentProcessor


class HTMLImageProcessor(HTMLComponentProcessor):
    def process(self, component: Component) -> Optional[str]:
        image = cast(Image, component)
        if image.image_format == ImageFormat.SVG:
            return image.image_data
        else:
            return f"<img src='data:image/{image.image_format.value};base64,{image.image_data}'/>"
