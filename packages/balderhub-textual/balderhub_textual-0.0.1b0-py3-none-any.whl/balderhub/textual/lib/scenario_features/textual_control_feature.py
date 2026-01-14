import balder
from balderhub.guicontrol.lib.scenario_features import GuiControlFeature

from balderhub.textual.lib.scenario_features.app_feature import AppFeature
from balderhub.textual.lib.utils.drivers.textual_driver_class import TextualDriverClass


class TextualControlFeature(GuiControlFeature):
    """
    Feature to control a textual application - necessary to interact with a textual application.
    """

    class App(balder.VDevice):
        """the app vdevice that provides the app instance under test"""
        app = AppFeature()

    @property
    def driver(self) -> TextualDriverClass:
        return super().driver

    def create(self) -> None:
        """
        creates the driver class to control the app - needs to be called within a fixture
        """
        self._driver = TextualDriverClass(self.App.app.get_app())
