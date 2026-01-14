import textual

from balderhub.textual.lib.scenario_features import AppFeature
from ...dut.calculator import CalculatorApp


class CalculatorAppFeature(AppFeature):

    def get_app(self) -> textual.app.App:
        return CalculatorApp()
