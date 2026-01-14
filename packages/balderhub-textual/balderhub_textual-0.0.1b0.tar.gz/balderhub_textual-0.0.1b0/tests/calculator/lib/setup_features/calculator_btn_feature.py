import time
from typing import Literal

from balderhub.textual.lib.scenario_features import TextualControlFeature
from .. import scenario_features
from ..pages.calculator_page import CalculatorPage


class CalculatorBtnFeature(scenario_features.CalculatorFeature):

    page_calculator = CalculatorPage()
    textual_control = TextualControlFeature()

    def press_buttons(self, numbers: list[str]):
        mapping = {
            "1": self.page_calculator.btn_1,
            "2": self.page_calculator.btn_2,
            "3": self.page_calculator.btn_3,
            "4": self.page_calculator.btn_4,
            "5": self.page_calculator.btn_5,
            "6": self.page_calculator.btn_6,
            "7": self.page_calculator.btn_7,
            "8": self.page_calculator.btn_8,
            "9": self.page_calculator.btn_9,
            ".": self.page_calculator.btn_point,
            "+": self.page_calculator.btn_plus,
            "-": self.page_calculator.btn_minus,
            "*": self.page_calculator.btn_multiply,
            "/": self.page_calculator.btn_divide,
            "=": self.page_calculator.btn_equals,
        }
        for cur_char in numbers:
            if cur_char not in mapping.keys():
                raise KeyError(f"Unexpected character {cur_char}")
            mapping[cur_char].click()
            time.sleep(0.3)

    def read_result(self) -> float:
        return float(self.page_calculator.numbers.raw_element.value)

    def do_calc(self, first_number: float, second_number: float, operator: Literal["+", "-", "*", "/"]) -> float:
        self.press_buttons([e for e in str(first_number)])
        self.press_buttons([operator])
        self.press_buttons([e for e in str(second_number)])
        self.press_buttons(["="])
        return self.read_result()
