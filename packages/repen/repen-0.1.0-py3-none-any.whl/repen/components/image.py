from enum import Enum

from repen.components.base import Component


class ImageFormat(Enum):
    BMP = "bmp"
    GIF = "gif"
    ICO = "ico"
    JPG = "jpg"
    PNG = "png"
    SVG = "svg"


class Image(Component):
    def __init__(self, image_data: str, image_format: ImageFormat, **metadata) -> None:
        super().__init__(**metadata)
        self.image_data = image_data
        self.image_format = image_format

    def copy(self) -> Component:
        return Image(self.image_data, self.image_format, **self.metadata)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} (format='{self.image_format.value}')"
