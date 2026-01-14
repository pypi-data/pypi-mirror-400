import balder

from balderhub.textual.lib.scenario_features.textual_control_feature import TextualControlFeature
from tests.calculator.lib.pages.calculator_page import CalculatorPage
from tests.calculator.lib.scenario_features.calculator_app_feature import CalculatorAppFeature
from tests.calculator.lib.setup_features import CalculatorBtnFeature, CalculatorKeysFeature


class SetupCalculator(balder.Setup):

    class App(balder.Device):
        app = CalculatorAppFeature()

    class ControllerOverButtons(balder.Device):
        textual = TextualControlFeature(App="App")
        page_calc = CalculatorPage()
        calc = CalculatorBtnFeature()

    class ControllerOverKeyPresses(balder.Device):
        textual = TextualControlFeature(App="App")
        page_calc = CalculatorPage()
        calc = CalculatorKeysFeature()

    @balder.fixture('testcase')
    def setup_app_btn(self):
        self.ControllerOverButtons.textual.create()
        yield
        self.ControllerOverButtons.textual.quit()

    @balder.fixture('testcase')
    def setup_app_keys(self):
        self.ControllerOverKeyPresses.textual.create()
        yield
        self.ControllerOverKeyPresses.textual.quit()