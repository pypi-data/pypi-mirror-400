from __future__ import annotations

from typing import Union

from textual.dom import DOMNode

from balderhub.gui.lib.utils.components.abstract_element import AbstractElement
from balderhub.gui.lib.utils.mixins import VisibleMixin
from balderhub.textual.lib.utils.drivers import TextualDriverClass
from balderhub.textual.lib.utils.element_bridges import TextualElementBridge

from ..selector import Selector


class TextualElement(AbstractElement, VisibleMixin):
    """
    The basic Textual Element
    """

    def __init__(self, bridge: TextualElementBridge):
        self._bridge = bridge

    def __eq__(self, other):
        return self.bridge == other.bridge

    @classmethod
    def by_selector(
            cls,
            driver: TextualDriverClass,
            selector: Selector,
            parent: Union[TextualElement, TextualElementBridge] = None
    ):
        """
        This method returns the element for the provided selector.

        :param driver: the textual driver
        :param selector: the selector to identify the element
        :param parent: optional a parent textual element, if the selector is relative
        :return: the textual element that is identified by the selector
        """
        if parent is None:
            bridge = driver.find_bridge(selector)
        else:
            if isinstance(parent, TextualElement):
                parent = parent.bridge
            bridge = parent.find_bridge(selector)
        return cls(bridge)

    @classmethod
    def by_raw_element(
            cls,
            driver: TextualDriverClass,
            raw_element: DOMNode,
            parent: Union[TextualElement, TextualElementBridge] = None
    ):
        """
        This method returns the textual element by the raw textual framework element.

        :param driver: the textual driver
        :param raw_element: the raw textual engine element (f.e. ``DOMNode`` or ``Widget``)
        :param parent: optional a parent textual element, if the selector is relative
        :return: the textual element that is identified by the selector
        """
        if parent is not None and isinstance(parent, TextualElement):
            parent = parent.bridge
        bridge = driver.get_bridge_for_raw_element(raw_element, parent)
        return cls(bridge)

    @property
    def bridge(self) -> TextualElementBridge:
        """
        :return: returns the underlying bridge object
        """
        return self._bridge

    @property
    def driver(self) -> TextualDriverClass:
        """
        :return: returns the underlying textual driver
        """
        return self._bridge.driver

    @property
    def raw_element(self) -> DOMNode:
        """
        :return: returns the raw textual engine element
        """
        return self._bridge.raw_element

    @property
    def parent_bridge(self) -> TextualElementBridge:
        """
        :return: returns the bridge of the parent element (if any)
        """
        return self._bridge.parent

    def exists(self) -> bool:
        return self._bridge.exists()

    def is_visible(self) -> bool:
        return self._bridge.is_visible()
