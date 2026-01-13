import base64
import io
import os
import re
from pathlib import Path, PurePath
from typing import Any, cast

from repen.adapters.base import ComponentAdapter
from repen.components import Component, Image, ImageFormat


class ImageAdapter(ComponentAdapter):
    def __init__(self, priority: int = 1) -> None:
        super().__init__(priority)

    def _bytes_to_base64(self, data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")


class PathImageAdapter(ImageAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if not isinstance(raw_data, (str, Path, PurePath)):
            return False

        try:
            path = Path(raw_data)
            if not path.exists():
                return False

            if not path.is_file():
                return False

            suffix = path.suffix.lower().lstrip(".")
            if not suffix:
                return False

            supported_formats = {fmt.value for fmt in ImageFormat}
            if suffix not in supported_formats:
                return False

            if not os.access(path, os.R_OK):
                return False

            return True
        except:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        path = Path(raw_data)
        suffix = path.suffix.lower().lstrip(".")
        image_format = ImageFormat(suffix)
        with open(path, "rb") as f:
            content = f.read()

        if image_format == ImageFormat.SVG:
            image_data = content.decode("utf-8")
        else:
            image_data = self._bytes_to_base64(content)

        return Image(image_data, image_format)


class BytesImageAdapter(ImageAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if not (isinstance(raw_data, bytes) and len(raw_data) > 0):
            return False

        try:
            self._detect_format_from_bytes(raw_data)
            return True
        except:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        content = raw_data
        image_format = self._detect_format_from_bytes(content)
        if image_format == ImageFormat.SVG:
            image_data = content.decode("utf-8")
        else:
            image_data = self._bytes_to_base64(content)

        return Image(image_data, image_format, **metadata)

    def _detect_format_from_bytes(self, data: bytes) -> ImageFormat:
        signatures = {
            b"\x89PNG\r\n\x1a\n": ImageFormat.PNG,
            b"\xff\xd8\xff": ImageFormat.JPG,
            b"GIF87a": ImageFormat.GIF,
            b"GIF89a": ImageFormat.GIF,
            b"BM": ImageFormat.BMP,
            b"<svg": ImageFormat.SVG,
            b"\x00\x00\x01\x00": ImageFormat.ICO,
        }
        for signature, image_format in signatures.items():
            if data.startswith(signature):
                return image_format

        raise ValueError("Could not identify image format from bytes")


class PillowImageAdapter(ImageAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        try:
            from PIL import Image as PILImage

            return isinstance(raw_data, PILImage.Image)
        except ImportError:
            return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        from PIL import Image as PILImage

        pil_image = cast(PILImage, raw_data)
        format_map = {
            "JPEG": ImageFormat.JPG,
            "PNG": ImageFormat.PNG,
            "GIF": ImageFormat.GIF,
            "BMP": ImageFormat.BMP,
            "ICO": ImageFormat.ICO,
        }
        pil_format = pil_image.format or "PNG"
        image_format = format_map.get(pil_format.upper(), ImageFormat.PNG)

        buffer = io.BytesIO()
        pil_image.save(buffer, format=pil_format)
        content = buffer.getvalue()

        image_data = self._bytes_to_base64(content)

        return Image(image_data, image_format, **metadata)


class SVGImageAdapter(ImageAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        if isinstance(raw_data, str):
            svg_match = re.search(r"<svg.*</svg>", str(raw_data), re.DOTALL)
            return True if svg_match else False
        return False

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        svg_content = str(raw_data)
        svg_match = re.search(r"<svg.*</svg>", svg_content, re.DOTALL)
        clean_svg = svg_match.group(0) if svg_match else svg_content
        return Image(clean_svg, ImageFormat.SVG, **metadata)
