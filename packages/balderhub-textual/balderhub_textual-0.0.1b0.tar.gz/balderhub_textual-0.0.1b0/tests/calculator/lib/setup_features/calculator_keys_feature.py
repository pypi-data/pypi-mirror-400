import time
from typing import Literal

from balderhub.textual.lib.scenario_features import TextualControlFeature
from .. import scenario_features
from ..pages.calculator_page import CalculatorPage


class CalculatorKeysFeature(scenario_features.CalculatorFeature):

    page_calculator = CalculatorPage()
    textual_control = TextualControlFeature()

    def press_buttons(self, numbers: list[str]):
        self.textual_control.driver.press(*numbers)

    def read_result(self) -> float:
        return float(self.page_calculator.numbers.raw_element.value)

    def do_calc(self, first_number: float, second_number: float, operator: Literal["+", "-", "*", "/"]) -> float:
        self.press_buttons([e for e in str(first_number)])
        self.press_buttons([operator])
        self.press_buttons([e for e in str(second_number)])
        self.press_buttons(["="])
        return self.read_result()
