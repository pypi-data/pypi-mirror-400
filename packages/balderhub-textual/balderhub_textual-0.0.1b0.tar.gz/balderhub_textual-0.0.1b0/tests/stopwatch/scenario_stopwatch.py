import datetime
import math
import time

import balder

from balderhub.textual.lib.scenario_features import TextualControlFeature

from .pages import StopwatchPage


class ScenarioStopWatch(balder.Scenario):

    class App(balder.Device):
        pass

    @balder.connect(App, over_connection=balder.Connection)
    class Controller(balder.Device):
        textual = TextualControlFeature()
        page = StopwatchPage()

    def test_start_stop(self):
        start_time = time.time()
        self.Controller.page.btn_start.click()
        time.sleep(1)
        self.Controller.page.btn_stop.click()
        expected_time = time.time() - start_time

        displayed_time = datetime.time.fromisoformat(self.Controller.page.numbers.get_value())

        displayed_sec = displayed_time.second + displayed_time.microsecond / 1_000_000

        assert displayed_time.hour == 0
        assert displayed_time.minute == 0
        # we are using this high deviation because of performance issues in Textual Pilot
        assert math.isclose(displayed_sec, expected_time, rel_tol=0.5), f"wrong time displayed: {displayed_sec} instead of {expected_time}"
