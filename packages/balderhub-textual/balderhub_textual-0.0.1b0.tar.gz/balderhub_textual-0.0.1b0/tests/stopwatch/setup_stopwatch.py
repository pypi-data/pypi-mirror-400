import balder

from .dut.stopwatch import StopwatchApp

from balderhub.textual.lib.scenario_features import TextualControlFeature, AppFeature
from .pages import StopwatchPage


class MyAppFeature(AppFeature):

    def get_app(self):
        return StopwatchApp()


class SetupStopwatch(balder.Setup):

    class App(balder.Device):
        app = MyAppFeature()

    @balder.connect(App, over_connection=balder.Connection)
    class Controller(balder.Device):
        textual = TextualControlFeature(App="App")
        page = StopwatchPage()

    @balder.fixture('testcase')
    def setup_app(self):
        self.Controller.textual.create()
        yield
        self.Controller.textual.quit()
