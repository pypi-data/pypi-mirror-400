from typing import Dict, Type

from repen.renderers.html.theme import HTMLTheme
from repen.renderers.html.theme_default import HTMLDefaultTheme


class HTMLThemeRegistry:
    def __init__(self):
        self._themes: Dict[str, Type[HTMLTheme]] = {}
        self._register_default_themes()

    def register(self, name: str, theme_class: Type[HTMLTheme]):
        self._themes[name] = theme_class

    def css(self, name: str) -> str:
        theme = self._theme(name)
        return theme.css()

    def _theme(self, theme_name: str) -> HTMLTheme:
        theme_class = self._themes.get(theme_name, HTMLDefaultTheme)
        return theme_class()

    def _register_default_themes(self):
        self.register("default", HTMLDefaultTheme)
