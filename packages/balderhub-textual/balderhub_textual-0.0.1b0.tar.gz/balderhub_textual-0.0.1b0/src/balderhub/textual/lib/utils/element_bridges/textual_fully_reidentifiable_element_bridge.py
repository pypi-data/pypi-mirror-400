from __future__ import annotations


from typing import TYPE_CHECKING, Optional, Union

from textual.dom import DOMNode

from ..selector import Selector
from .textual_element_bridge import TextualElementBridge


if TYPE_CHECKING:
    from ..drivers.textual_driver_class import TextualDriverClass
    from ..components.textual_element import TextualElement


class TextualFullyReidentifiableElementBridge(TextualElementBridge):
    """
    A fully reidentifiable element bridge specifies the element in an absolute manner. It doesn't matter if the element
    has a full absolute selector or has parents with re-identifiable selectors (so all parents need to be
    :class:`FullyReidentifiableElementBridge` objects)
    """

    def __init__(
            self,
            driver: TextualDriverClass,
            selector: Selector,
            parent: Optional[TextualFullyReidentifiableElementBridge] = None
    ):
        super().__init__(driver=driver, parent=parent)
        self._selector = selector

    def __eq__(self, other):
        if not isinstance(other, TextualFullyReidentifiableElementBridge):
            raise TypeError(f'can not compare elements from different bridge type (this is {self.__class__} '
                            f'| other is {other.__class__})')
        if self.parent != other.parent:
            return False
        if self.selector != other.selector:
            return False
        return True

    @property
    def raw_element(self) -> TextualElement:
        if self._raw_element is None:
            self.re_identify_raw_element()
        return self._raw_element

    @property
    def parent(self) -> Union[TextualFullyReidentifiableElementBridge, None]:
        return super().parent

    @property
    def selector(self) -> Selector:
        """
        :return: the absolute selector this element bridge has.
        """
        return self._selector

    def re_identify_raw_element(self) -> DOMNode:
        """
        This method re-identifies the element by requesting it again from the main driver. This method automatically
        updates the internal reference for this object.

        :return: the re-identified raw element
        """
        if self.parent is None:
            self._raw_element = self.driver.find_raw_element(self.selector)
        else:
            self._raw_element = self.parent.find_raw_element(self.selector)
        return self._raw_element

    def find_bridge(self, selector: Selector) -> TextualFullyReidentifiableElementBridge:
        return TextualFullyReidentifiableElementBridge(self.driver, selector, parent=self)

    def exists(self) -> bool:
        if self.parent is None:
            if self.driver.find_raw_element(self.selector):
                return True
        else:
            if self.parent.find_raw_element(self.selector):
                return True

        return False
