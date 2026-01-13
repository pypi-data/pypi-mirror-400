from typing import Optional, Set, cast

from repen.components import (Component, Composite, Text, TextBlock, TextStyle,
                              TextVariant)
from repen.renderers.html.processor import (HTMLComponentProcessor,
                                            HTMLCompositeProcessor)


class HTMLTextProcessor(HTMLComponentProcessor):
    def process(self, component: Component) -> Optional[str]:
        text = cast(Text, component)
        class_str = self._style_to_classes(text.styles)
        if class_str:
            return f"<span class='{class_str}'>{text.content}</span>"
        else:
            return text.content

    def _style_to_classes(self, styles: Set[TextStyle]) -> str:
        mapping = {
            TextStyle.BOLD: "bold",
            TextStyle.ITALIC: "italic",
            TextStyle.UNDERLINE: "underline",
            TextStyle.STRIKETHROUGH: "strikethrough",
            TextStyle.CODE: "code",
        }
        if len(styles) > 0:
            classes = [mapping.get(s, "") for s in styles]
            return " ".join(classes)
        return ""


class HTMLTextBlockProcessor(HTMLCompositeProcessor):
    def begin(self, composite: Composite) -> Optional[str]:
        text_block = cast(TextBlock, composite)
        tag = self._variant_to_tag(text_block.variant)
        return f"<{tag}>"

    def end(self, composite: Composite) -> Optional[str]:
        text_block = cast(TextBlock, composite)
        tag = self._variant_to_tag(text_block.variant)
        return f"</{tag}>"

    def _variant_to_tag(self, variant: TextVariant) -> str:
        mapping = {
            TextVariant.HEADING_1: "h1",
            TextVariant.HEADING_2: "h2",
            TextVariant.HEADING_3: "h3",
            TextVariant.HEADING_4: "h4",
            TextVariant.HEADING_5: "h5",
            TextVariant.HEADING_6: "h6",
            TextVariant.PARAGRAPH: "p",
        }
        return mapping.get(variant, "p")


class HTMLTextSpanProcessor(HTMLCompositeProcessor):
    pass


class HTMLTextLinesProcessor(HTMLCompositeProcessor):
    def end_child(
        self,
        composite: Composite,
        component: Component,
    ) -> Optional[str]:
        return "</br>"
