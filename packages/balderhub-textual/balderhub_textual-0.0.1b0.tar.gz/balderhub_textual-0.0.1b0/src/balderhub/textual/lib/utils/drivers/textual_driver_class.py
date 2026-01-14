from typing import Optional

import asyncio
import textual

from textual.dom import DOMNode
from textual.pilot import Pilot
from textual.widget import Widget

from balderhub.guicontrol.lib.utils.driver import BaseDriverClass
from balderhub.textual.lib.utils.selector import Selector
from balderhub.textual.lib.utils.element_bridges import \
    TextualElementBridge, TextualNotReidentifiableElementBridge, TextualFullyReidentifiableElementBridge



class TextualDriverClass(BaseDriverClass):
    """main textual driver class"""

    def __init__(self, app_instance: textual.app.App):
        self._app_instance = app_instance

        self._async_runner_cm = asyncio.Runner()
        self._async_runner = self._async_runner_cm.__enter__()

        self._async_pilot_cm = self._app_instance.run_test()

        self._pilot_instance = self._enter_pilot()

    def _enter_pilot(self) -> Pilot:

        async def run_query():
            await asyncio.sleep(0)
            pilot = await self._async_pilot_cm.__aenter__() # pylint: disable=unnecessary-dunder-call
            await asyncio.sleep(0)
            return pilot

        return self._async_runner.run(run_query())

    def get_bridge_for_raw_element(
            self,
            raw_element: DOMNode,
            parent: Optional[TextualElementBridge] = None
    ) -> TextualNotReidentifiableElementBridge:
        """
        This method returns the bridge object for a raw textual element.

        :param raw_element: the raw textual element
        :param parent: the parent bridge of the element that is a parent of this element (or None if there is no parent
                       specified)
        :return: the newly created bridge object
        """
        return TextualNotReidentifiableElementBridge(self, raw_element, parent=parent)

    def find_raw_element(self, selector: Selector) -> DOMNode:
        """
        This method returns the raw textual element that matches the given selector.

        :param selector: the selector to match
        """
        return self._app_instance.query_one(selector.to_textual_string())

    def find_raw_elements(self, selector: Selector) -> list[DOMNode]:
        """
        This method returns all matching raw textual elements that match the given selector.

        :param selector: the selector to match
        """
        return list(self._app_instance.query(selector.to_textual_string()))

    def find_bridge(self, selector: Selector) -> TextualFullyReidentifiableElementBridge:
        return TextualFullyReidentifiableElementBridge(self, selector, parent=None)

    def find_bridges(self, selector: Selector) -> list[TextualNotReidentifiableElementBridge]:
        items = []
        for cur_web_element in self.find_raw_elements(selector.to_textual_string()):
            items.append(self.get_bridge_for_raw_element(raw_element=cur_web_element, parent=None))
        return items

    def _shutdown_pilot(self) -> None:
        exc = (None, None, None)

        async def execute_shutdown():
            await asyncio.sleep(0)
            await self._async_pilot_cm.__aexit__(*exc)

        try:
            self._async_runner.run(execute_shutdown())
        finally:
            self._async_runner_cm.__exit__(*exc)
            self._async_runner = None
            self._async_runner_cm = None

            self._async_pilot_cm = None
            self._pilot_instance = None

    def quit(self):
        if self._pilot_instance is not None:
            self._shutdown_pilot()

    def click(self, widget: Widget):
        """
        Executes a mouse click on the given widget
        """
        return self._async_runner.run(self._pilot_instance.click(widget))

    def press(self, *keys: str):
        """
        This method executes key presses within the application.

        :param keys: the keys to press
        """
        return self._async_runner.run(self._pilot_instance.press(*keys))
