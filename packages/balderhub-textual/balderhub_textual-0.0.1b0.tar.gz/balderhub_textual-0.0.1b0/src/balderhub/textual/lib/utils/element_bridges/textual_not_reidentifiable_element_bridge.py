from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

from textual.dom import DOMNode

from ..selector import Selector
from .textual_element_bridge import TextualElementBridge


if TYPE_CHECKING:
    from ..drivers.textual_driver_class import TextualDriverClass
    from .textual_partly_reidentifiable_element_bridge import TextualPartlyReidentifiableElementBridge


class TextualNotReidentifiableElementBridge(TextualElementBridge):
    """
    A non reidentifiable element bridge can not re-identify an element by itself, because it does not specify absolute
    selectors.
    """

    def __init__(
            self,
            driver: TextualDriverClass,
            raw_element: DOMNode,
            parent: Optional[TextualElementBridge] = None
    ):
        super().__init__(driver=driver, parent=parent)
        self._raw_element = raw_element

    def __eq__(self, other):
        raise TypeError('can not compare elements that were created out of web elements')

    def find_bridge(self, selector: Selector) -> TextualPartlyReidentifiableElementBridge:
        # pylint: disable-next=import-outside-toplevel
        from .textual_partly_reidentifiable_element_bridge import TextualPartlyReidentifiableElementBridge

        return TextualPartlyReidentifiableElementBridge(self.driver, selector, parent=self)

    @property
    def parent(self) -> Union[TextualElementBridge, None]:
        return self._parent

    def exists(self):
        return self.raw_element.display
