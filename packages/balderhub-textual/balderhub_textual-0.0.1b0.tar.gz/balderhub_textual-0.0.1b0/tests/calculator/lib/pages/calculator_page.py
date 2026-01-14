from balderhub.textual.lib.scenario_features.textual_page import TextualPage
from balderhub.textual.lib.utils import components
from balderhub.textual.lib.utils.selector import Selector


class CalculatorPage(TextualPage):

    @property
    def numbers(self) -> components.widgets.Digits:
        return components.widgets.Digits.by_selector(self.driver, Selector.by_id('numbers'))

    @property
    def btn_1(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-1'))

    @property
    def btn_2(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-2'))

    @property
    def btn_3(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-3'))

    @property
    def btn_4(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-4'))

    @property
    def btn_5(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-5'))

    @property
    def btn_6(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-6'))

    @property
    def btn_7(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-7'))

    @property
    def btn_8(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-8'))

    @property
    def btn_9(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('number-9'))

    @property
    def btn_ac(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('ac'))

    @property
    def btn_c(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('c'))

    @property
    def btn_plus_minus(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('plus-minus'))

    @property
    def btn_percent(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('percent'))

    @property
    def btn_divide(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('divide'))

    @property
    def btn_multiply(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('multiply'))

    @property
    def btn_minus(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('minus'))

    @property
    def btn_plus(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('plus'))

    @property
    def btn_point(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('point'))

    @property
    def btn_equals(self) -> components.widgets.Button:
        return components.widgets.Button.by_selector(self.driver, Selector.by_id('equals'))

