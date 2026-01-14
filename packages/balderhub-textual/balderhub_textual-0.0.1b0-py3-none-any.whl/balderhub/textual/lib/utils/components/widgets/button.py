from balderhub.gui.lib.utils.mixins import ClickableMixin, RectangleMixin

from ..textual_element import TextualElement


class Button(TextualElement, ClickableMixin, RectangleMixin):
    """
    A textual Button object (see: https://textual.textualize.io/widgets/button/)
    """
    def is_clickable(self) -> bool:
        return self._bridge.is_clickable()

    def click(self) -> None:
        self.bridge.click()

    @property
    def width(self) -> float:
        return self.bridge.get_rect()[2]

    @property
    def height(self) -> float:
        return self.bridge.get_rect()[3]
