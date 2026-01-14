import balder

from tests.calculator.lib.scenario_features import CalculatorFeature


class ScenarioCalculator(balder.Scenario):

    class Calculator(balder.Device):
        calc = CalculatorFeature()

    @balder.parametrize('data_tuple', [
        (1, 2, 3),
        (-4.2, 2.2, -2),
        (1.111111111111111, 1.111111111111111, 2.222222222222222),
        (4, 2.8, 6.8),
        (1, 1, 2),
    ])
    def test_add(self, data_tuple: tuple):
        first_no, second_no, expected_result = data_tuple

        result = self.Calculator.calc.do_calc(first_no, second_no, '+')
        assert result == expected_result, f"got different result: {result} (expected {expected_result})"
