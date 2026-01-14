from __future__ import annotations

from typing import Union, TYPE_CHECKING

from ..selector import Selector
from .textual_element_bridge import TextualElementBridge


if TYPE_CHECKING:
    from ..drivers.textual_driver_class import TextualDriverClass
    from ..components.textual_element import TextualElement
    from .textual_not_reidentifiable_element_bridge import TextualNotReidentifiableElementBridge


class TextualPartlyReidentifiableElementBridge(TextualElementBridge):
    """
    A partly reidentifiable element bridge specifies a bridge that does only have a relative selector to another bridge
    object that is not re-identifiable. This type of bridges are only reidentifiable if their parent element is in a
    reliable state.
    """
    def __init__(
            self,
            driver: TextualDriverClass,
            relative_selector: Selector,
            parent: Union[TextualPartlyReidentifiableElementBridge, TextualNotReidentifiableElementBridge]
    ):
        super().__init__(driver=driver, parent=parent)
        self._relative_selector = relative_selector

    def __eq__(self, other):
        if not isinstance(other, TextualPartlyReidentifiableElementBridge):
            raise TypeError(f'can not compare elements from different bridge type (this is {self.__class__} '
                            f'| other is {other.__class__})')
        if self.parent != other.parent:
            return False
        if self.relative_selector != other.relative_selector:
            return False
        return True

    @property
    def raw_element(self) -> TextualElement:
        if self._raw_element is None:
            self.re_identify_raw_element()
        return self._raw_element

    @property
    def parent(self) -> Union[TextualPartlyReidentifiableElementBridge, TextualNotReidentifiableElementBridge, None]:
        return super().parent

    def re_identify_raw_element(self) -> TextualElement:
        """
        This method re-identifies the element by requesting it again from the main driver. This method automatically
        updates the internal reference for this object.

        :return: the re-identified raw element
        """
        self._raw_element = self.parent.find_raw_element(self.relative_selector)
        return self._raw_element

    @property
    def relative_selector(self) -> Selector:
        """
        :return: returns the relative selector.
        """
        return self._relative_selector

    def find_bridge(self, selector: Selector) -> TextualPartlyReidentifiableElementBridge:
        return TextualPartlyReidentifiableElementBridge(self.driver, selector, parent=self)


    def exists(self) -> bool:
        if self.parent.find_raw_element(self.relative_selector):
            return True
        return False
