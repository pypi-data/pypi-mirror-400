from abc import ABC, abstractmethod
from typing import Dict


class HTMLTheme(ABC):
    def __init__(self):
        self._variables = self.variables()
        self._styles = self.styles()

    @abstractmethod
    def variables(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def styles(self) -> str:
        pass

    def css(self) -> str:
        css_vars = ":root {\n"
        for key, value in self._variables.items():
            css_vars += f"  --{key}: {value};\n"
        css_vars += "}\n\n"

        return css_vars + self._styles

    def __str__(self) -> str:
        return self.css()
