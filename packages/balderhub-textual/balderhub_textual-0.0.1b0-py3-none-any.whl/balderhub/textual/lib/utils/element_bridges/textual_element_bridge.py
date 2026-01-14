from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, List, Optional, TYPE_CHECKING, TypeVar

from textual.containers import VerticalScroll, HorizontalScroll, ScrollableContainer
from textual.dom import DOMNode
from textual.widget import Widget
from textual.widgets import Button, Label, Input, TextArea, Select, Digits

from balderhub.guicontrol.lib.utils.element_bridges.base_element_bridge import BaseElementBridge


from ..selector import Selector


if TYPE_CHECKING:
    from ..drivers import TextualDriverClass
    from .textual_fully_reidentifiable_element_bridge import TextualFullyReidentifiableElementBridge
    from .textual_partly_reidentifiable_element_bridge import TextualPartlyReidentifiableElementBridge
    from .textual_not_reidentifiable_element_bridge import TextualNotReidentifiableElementBridge

DOMNodeTypeT = TypeVar("DOMNodeTypeT", bound=DOMNode)


class TextualElementBridge(BaseElementBridge, ABC):
    """
    basic web-element-bridge implementation for Textual Elements
    """

    def __init__(self, driver: TextualDriverClass, parent: Optional[TextualElementBridge]):
        """
        Creates a new instance

        :param driver: the base driver class
        :param parent: the parent web element bridge (if this element has a parent element)
        """
        super().__init__(driver, parent)

    @property
    def driver(self) -> TextualDriverClass:
        """
        :return: returns the driver class, this bridge was created from
        """
        return self._driver

    @property
    def raw_element(self) -> DOMNodeTypeT:
        return super(self).raw_element

    @property
    def parent(self) -> Union[TextualElementBridge, None]:
        """
        :return: returns the defined parent web element bridge if a parent does exist
        """
        return self._parent

    def find_raw_element(self, selector: Selector) -> DOMNodeTypeT:
        """
        Method to find a specific raw web element by its selector that is a child of the current one

        :param selector: the selector specifying the element (relative to this one)
        :return: the raw web element (depending on the underlying framework)
        """
        result = self.raw_element.query_one(selector.to_textual_string())
        if result is None:
            raise ValueError(f'no such element with selector `{selector}`')
        return result

    def find_raw_elements(self, selector: Selector) -> List[DOMNodeTypeT]:
        """
        Method to find raw web elements matching the provided relative selector as a child of the current one

        :param selector: the selector specifying the elements (relative to this one)
        :return: the raw web element (depending on the underlying framework)
        """
        return list(self.raw_element.query(selector.to_textual_string()))

    @abstractmethod
    def find_bridge(
            self,
            selector: Selector
    ) -> Union[TextualFullyReidentifiableElementBridge, TextualPartlyReidentifiableElementBridge]:
        """
        Method to directly returning the bridge of a specific raw web element by its selector that is a child of the
        current one. In case that the element can be reidentified completely by the selector (f.e. because the selector
        is By.ID) the method returns a :class:`FullyReidentifiableElementBridge` object. Otherwise, the method returns
        a :class:`PartlyReidentifiableElementBridge` object.

        :param selector: the selector specifying the element (relative to this one)
        :return: the bridge object of the element specified by the selector
        """

    def find_bridges(self, selector: Selector) -> List[TextualNotReidentifiableElementBridge]:
        """
        Method to directly returning a list of bridge objects for raw web elements matching the provided relative
        selector as a child of the current one

        :param selector: the selector specifying the elements (relative to this one)
        :return: a list with all matching bridge objects (depending on the underlying framework)
        """
        # pylint: disable-next=import-outside-toplevel
        from .textual_not_reidentifiable_element_bridge import TextualNotReidentifiableElementBridge
        result = []
        for cur_elem in self.find_raw_elements(selector):
            result.append(TextualNotReidentifiableElementBridge(self.driver, cur_elem, parent=self))
        return result

    def exists(self) -> bool:
        """
        This method returns True if the element exists. An element exists if it is still part of the DOM.

        .. note::
            This does not mean, that it needs to be visible! Use the :meth:`BaseWebElementBridge.is_visible` method
            instead.`

        :return: returns True if the element does exist otherwise false.
        """
        return self.raw_element.display

    def is_visible(self) -> bool:
        """
        This method returns True if the element is visible.

        :return: returns True if the element is visible otherwise false.
        """
        return self.raw_element.visible

    def is_disabled(self) -> bool:
        """
        This method returns True if the element is visible.

        :return: returns True if the element does exist otherwise false.
        """
        return hasattr(self.raw_element, 'is_disabled') and self.raw_element.is_disabled

    def get_text_content(self) -> str:
        """
        This method returns the text of the element as a string.

        :return: returns the text of the element as a string
        """
        elem = self.raw_element
        if isinstance(elem, (Label, TextArea)):
            return elem.text
        if isinstance(elem, Button):
            return elem.label
        if isinstance(elem, (Input, Select, Digits)):
            return elem.value
        raise NotImplementedError(f'this method is not supported for widgets of type {elem}')

    def is_clickable(self) -> bool:
        """
        This method returns True if the element is (theoretically) clickable.

        :return: returns True if the element is (theoretically) clickable, otherwise False.
        """
        elem = self.raw_element
        if not isinstance(elem, (Button, Label)):
            return False
        return not self.is_visible() and elem.can_focus and hasattr(elem, 'on_click')

    ########################################################################################################
    # STATE
    ########################################################################################################

    def is_selected(self) -> bool:
        """
        The Is Element Selected command determines if the referenced element is selected or not. This operation only
        makes sense on input elements of the Checkbox- and Radio Button states, or on option elements.

        :return: returns True if the element is selected.
        """
        elem = self.raw_element
        if not isinstance(elem, Select):
            raise NotImplementedError(f'this method is not supported for widgets of type {self.raw_element}')
        return elem.selection is not None

    def get_rect(self) -> tuple[int, int, int, int]:
        """
        :return: the rect of the element (x, y, width, height)
        """
        elem = self.raw_element
        if isinstance(elem, Widget):
            return elem.region.x, elem.region.y, elem.region.width, elem.region.height
        raise NotImplementedError(f'this method is not supported for elements of type {self.raw_element}')

    ########################################################################################################
    # INTERACTIONS
    ########################################################################################################

    def click(self) -> None:
        """
        This method clicks the element.

        The Element Click command scrolls into view the element if it is not already pointer-interactable, and clicks
        its in-view center point.

        If the element's center point is obscured by another element, an element click intercepted error is returned.
        If the element is outside the viewport, an element not interactable error is returned.
        """
        self.driver.click(self.raw_element)

    def clear(self):
        """
        Clears the element
        """
        elem = self.raw_element
        if isinstance(elem, (Input, TextArea)):
            elem.clear()
        raise NotImplementedError(f'this method is not supported for widgets of type {self.raw_element}')

    def send_keys(self, text: str) -> None:
        """
        This method inserts a text into the field.

        The Element Send Keys command scrolls into view the form control element and then sends the provided keys to
        the element. In case the element is not keyboard-interactable, an element not interactable error is returned.

        :param text: the text that should be inserted into the field
        """
        self.driver.press(*text)

    def select_by_text(self, text_of_option_to_select: str) -> None:
        """
        This method selects the element by shown text.
        :param text_of_option_to_select: the expected text in the option that should be selected
        """
        elem = self.raw_element
        if not isinstance(elem, Select):
            raise NotImplementedError(f'this method is not supported for widgets of type {self.raw_element}')

        for label, value in elem.options:
            if label == text_of_option_to_select:
                elem.value = value
                break
        else:
            raise ValueError(f'can not find an option with the provided text `{text_of_option_to_select}`')

    def select_by_option_index(self, index: int) -> None:
        """
        This method selects the element by index.
        :param index: the option index that should be selected
        """
        elem = self.raw_element
        if not isinstance(elem, Select):
            raise NotImplementedError(f'this method is not supported for widgets of type {self.raw_element}')

        elem.value = elem.options[index][1]

    def select_by_option_value(self, value: str):
        """
        This method selects the element by value.
        :param value: the option value that should be selected
        """
        elem = self.raw_element
        if not isinstance(elem, Select):
            raise NotImplementedError(f'this method is not supported for widgets of type {self.raw_element}')
        elem.value = value

    def scroll_to_beginning(self):
        """
        This method scrolls to the beginning of the scrollable element. It needs to make sure, that after calling it,
        the scrollable element is always at the beginning of its content. It raises an error, in case the element can
        not be scrolled.
        """
        elem = self.raw_element
        if isinstance(elem, ScrollableContainer):
            elem.scroll_home(animate=False)
        raise ValueError(f'this method is only supported for widgets of class {ScrollableContainer.__name__}')

    def scroll_for(self, scroll_steps: int):
        """
        This method scrolls for one row / column.

        :param scroll_steps: the number of steps to scroll (positive: scrolls forward, negative: scrolls backward)
        """
        elem = self.raw_element

        if isinstance(elem, VerticalScroll):
            elem.scroll_relative(y=scroll_steps)
        elif isinstance(elem, HorizontalScroll):
            elem.scroll_relative(x=scroll_steps)
        else:
            raise ValueError(f'this method is only supported for widgets of class {VerticalScroll.__name__} or '
                             f'{HorizontalScroll.__name__}')

    def scroll_to_end(self):
        """
        This method scrolls to the end of the scrollable element.  It needs to make sure, that after calling it, the
        scrollable element is always at the end of its content. It raises an error, in case the element can not
        be scrolled.
        """
        elem = self.raw_element
        if isinstance(elem, ScrollableContainer):
            elem.scroll_home(animate=False)
        raise ValueError(f'this method is only supported for widgets of class {ScrollableContainer.__name__}')
