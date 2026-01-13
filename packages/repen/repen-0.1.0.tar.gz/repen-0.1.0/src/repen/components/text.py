from abc import ABC
from enum import Enum
from typing import Optional, Set

from repen.components.base import Component, Composite


class TextVariant(Enum):
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    HEADING_4 = "heading_4"
    HEADING_5 = "heading_5"
    HEADING_6 = "heading_6"

    PARAGRAPH = "paragraph"


class TextStyle(Enum):
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    CODE = "code"


class TextLike(Component, ABC):
    pass


class Text(TextLike):
    def __init__(
        self,
        content: str,
        styles: Optional[Set[TextStyle]] = None,
        **metadata,
    ) -> None:
        super().__init__(**metadata)
        self.content: str = content
        self.styles: Set[TextStyle] = styles or set()

    def copy(self) -> Component:
        return Text(self.content, self.styles, **self.metadata)

    def __repr__(self) -> str:
        style_str = ", ".join(s.value for s in self.styles)
        content_preview = self.content[: min(30, len(self.content))]
        return f"{self.__class__.__name__} (content='{content_preview}{'...' if len(self.content) > 30 else ''}', styles=[{style_str}])"


class TextBlock(TextLike, Composite):
    def __init__(self, variant: TextVariant, **metadata) -> None:
        super().__init__(**metadata)
        self.variant = variant

    def copy(self) -> Component:
        return TextBlock(self.variant, **self.metadata)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} (variant={self.variant.value})"


class TextSpan(TextLike, Composite):
    pass


class TextLines(TextLike, Composite):
    pass


class TextSection(TextLike, Composite):
    pass
