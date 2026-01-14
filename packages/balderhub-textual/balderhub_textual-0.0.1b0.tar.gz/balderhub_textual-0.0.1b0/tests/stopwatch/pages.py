from balderhub.textual.lib.scenario_features import TextualPage
from balderhub.textual.lib.utils import components
from balderhub.textual.lib.utils.selector import Selector


class StopwatchPage(TextualPage):
    """
    This page represents the stopwatch screen in your Textual app.
    It defines properties for key widgets like the time display and buttons.
    """

    @property
    def numbers(self) -> components.widgets.Digits:
        """
        Returns the time display widget.
        Assumes it's a Digits widget with a tag 'TimeDisplay'.
        """
        return components.widgets.Digits.by_selector(self.driver, Selector.by_tag('TimeDisplay'))

    @property
    def btn_start(self) -> components.widgets.Button:
        """
        Returns the 'Start' button by its ID.
        """
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('start'))

    @property
    def btn_stop(self) -> components.widgets.Button:
        """
        Returns the 'Stop' button by its ID.
        """
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('stop'))

    @property
    def btn_reset(self) -> components.widgets.Button:
        """
        Returns the 'Reset' button by its ID.
        """
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('reset'))