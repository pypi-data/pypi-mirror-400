import time
import balderhub.gui.lib.scenario_features
import balderhub.guicontrol.lib.scenario_features

import balderhub.textual.lib.utils.drivers


class TextualPage(balderhub.gui.lib.scenario_features.PageFeature):
    """
    Page object for textual application screens
    """

    guicontrol = balderhub.guicontrol.lib.scenario_features.GuiControlFeature()

    @property
    def driver(self) -> balderhub.textual.lib.utils.drivers.TextualDriverClass:
        """
        Returns the driver instance
        """
        return self.guicontrol.driver

    @property
    def applicable_on_screen_id(self) -> str:
        """
        Should return the screen id - is used to determine which screen is active at the moment
        """
        raise NotImplementedError

    def is_applicable(self):
        """
        Returns true if the current screen is the expected one (see :meth:`TextualPage.applicable_on_screen_id`)
        """
        # how should that be terminated?
        return self.driver.pilot_instance.app.screen.id == self.applicable_on_screen_id

    def wait_till_applicable(self, timeout=5):
        """
        Waits until the expected screen is active (default timeout is 5 seconds)
        """
        start_time = time.perf_counter()
        all_visibilities = []
        while True:
            current_screen_id = self.driver.pilot_instance.app.screen.id
            if current_screen_id == self.applicable_on_screen_id:
                # found it
                return
            if current_screen_id not in all_visibilities:
                all_visibilities.append(current_screen_id)
            time.sleep(0.1)
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f'expected page with activity `{self.applicable_on_screen_id}` is not applicable '
                                   f'within timeout of {timeout} seconds (following activities were visible while '
                                   f'waiting: {all_visibilities}`')
