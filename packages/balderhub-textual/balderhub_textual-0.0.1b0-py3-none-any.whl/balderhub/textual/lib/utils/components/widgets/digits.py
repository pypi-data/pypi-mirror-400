from balderhub.gui.lib.utils.mixins import HasValueMixin

from ..textual_element import TextualElement


class Digits(TextualElement, HasValueMixin):
    """
    A textual Digits object (see: https://textual.textualize.io/widgets/digits/)
    """

    def get_value(self) -> str:
        return self.bridge.get_text_content()
