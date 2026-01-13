import re
from typing import Any, Optional

from repen.adapters.base import ComponentAdapter
from repen.components import (Component, Text, TextBlock, TextLines,
                              TextSection, TextStyle, TextVariant)
from repen.components.text import TextSpan


class TextAdapter(ComponentAdapter):
    def can_adapt(self, raw_data: Any, **metadata: Any) -> bool:
        return isinstance(raw_data, str)

    def adapt(self, raw_data: Any, **metadata: Any) -> Component:
        text = str(raw_data)

        # Empty string - skip
        if not text:
            return Text("", **metadata)

        paragraphs = re.split(r"\n\n", text)
        if len(paragraphs) == 1:
            return self._parse_paragraph(paragraphs[0], **metadata)

        stack = TextSection(**metadata)
        for paragraph in paragraphs:
            stack.add(self._parse_paragraph(paragraph, **metadata))
        return stack

    def _parse_paragraph(self, text: str, **metadata) -> Component:
        lines = [line.strip() for line in text.split("  \n")]
        if len(lines) == 1:
            return self._parse_line(lines[0], **metadata)

        lines_component = TextLines(**metadata)
        for line in lines:
            lines_component.add(self._parse_inline(line, **metadata))

        block = TextBlock(TextVariant.PARAGRAPH, **metadata)
        block.add(lines_component, **metadata)
        return block

    def _parse_line(self, line: str, **metadata) -> Component:
        heading_match = re.match(r"^(#+)\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            variant_map = {
                1: TextVariant.HEADING_1,
                2: TextVariant.HEADING_2,
                3: TextVariant.HEADING_3,
                4: TextVariant.HEADING_4,
                5: TextVariant.HEADING_5,
            }
            variant = variant_map.get(level, TextVariant.HEADING_6)
            block = TextBlock(variant, **metadata)
            block.add(self._parse_inline(content, **metadata))
            return block

        block = TextBlock(TextVariant.PARAGRAPH, **metadata)
        block.add(self._parse_inline(line, **metadata))
        return block

    def _simplify_component(self, component: Component, **metadata) -> Component:
        if isinstance(component, TextSpan):
            if len(component.children) == 1:
                return component.children[0]

            texts = []
            same_styles = None
            all_text = True

            for child in component.children:
                if isinstance(child, Text):
                    texts.append(child.content)
                    if same_styles is None:
                        same_styles = child.styles.copy() if child.styles else set()
                    elif child.styles != same_styles:
                        all_text = False
                        break
                else:
                    all_text = False
                    break

            if all_text and texts:
                return Text("".join(texts), same_styles, **metadata)

        return component

    def _is_text_start_with_delimiter_at_position(
        self, text: str, pos: int
    ) -> Optional[str]:
        delimiters = ["**", "__", "~~", "++", "*", "_", "`"]
        for delim in delimiters:
            if text.startswith(delim, pos):
                return delim
        return None

    def _parse_inline(self, text: str, **metadata) -> Component:
        stack = []  # (delimeter, span, styles)
        root = TextSpan(**metadata)
        i = 0
        n = len(text)
        current_text = ""
        current_parent = root
        while i < n:
            delimiter = self._is_text_start_with_delimiter_at_position(text, i)
            if delimiter:
                is_code = False
                is_closing = False
                if stack:
                    current_delimiter = stack[-1][0]
                    if delimiter.startswith(current_delimiter):
                        delimiter = current_delimiter
                    is_closing = current_delimiter == delimiter
                    if current_delimiter == "`" and not is_closing:
                        is_code = True

                if is_code:
                    i += len(delimiter)
                    continue

                if current_text:
                    if stack:
                        _, _, styles = stack[-1]
                        current_parent.add(
                            Text(current_text, styles.copy(), **metadata)
                        )
                    else:
                        current_parent.add(Text(current_text, **metadata))
                    current_text = ""

                if is_closing:
                    _, span, _ = stack.pop()
                    if stack:
                        current_parent = stack[-1][1]
                    else:
                        current_parent = root
                    current_parent.add(self._simplify_component(span, **metadata))
                else:
                    styles = stack[-1][2].copy() if stack else set()
                    if delimiter in ["**", "__"]:
                        styles.add(TextStyle.BOLD)
                    elif delimiter in ["*", "_"]:
                        styles.add(TextStyle.ITALIC)
                    elif delimiter == "~~":
                        styles.add(TextStyle.STRIKETHROUGH)
                    elif delimiter == "++":
                        styles.add(TextStyle.UNDERLINE)
                    elif delimiter == "`":
                        styles.add(TextStyle.CODE)

                    new_span = TextSpan(**metadata)
                    stack.append((delimiter, new_span, styles))
                    current_parent = new_span

                i += len(delimiter)
            else:
                current_text += text[i]
                i += 1

        # Rest of the text
        if current_text:
            if stack:
                _, _, styles = stack[-1]
                current_parent.add(Text(current_text, styles.copy(), **metadata))
            else:
                current_parent.add(Text(current_text, **metadata))
            current_text = ""

        return self._simplify_component(root, **metadata)
