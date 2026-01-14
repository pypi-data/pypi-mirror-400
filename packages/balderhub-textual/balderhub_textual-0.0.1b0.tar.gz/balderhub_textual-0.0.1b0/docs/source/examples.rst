Examples
********

The core idea in Balder is to define "features" and "devices" that represent parts of your system. For Textual testing,
BalderHub provides ready-made features like :class:`TextualControlFeature` (for controlling the app) and `TextualPage`
(that allows to write tests according the Page-Object-Model).

Application-Under-Test
======================

In this example section we want to test a Stopwatch application, similar to the
`Textuals-Tutorial section <https://textual.textualize.io/tutorial/>`__.

You can find the code of this application at
`the GitHub Repository <http://github.com/balder-dev/balderhub-textual/blob/main/tests/stopwatch/dut>`_.

Basic Setup
===========

Start by creating a setup file (e.g., ``setup_stopwatch.py``).

Here's how to configure the minimum required elements:

* Import the necessary modules from Balder and BalderHub.
* Define a custom ``AppFeature`` class that returns your Textual app instance.
* Create a Setup class with two devices: one for the app itself and one for the controller that interacts with it.

In code, this looks like shown below:

.. code-block:: python

    # file `setup_stopwatch.py`

    import balder

    from balderhub.textual.lib.scenario_features import TextualControlFeature, AppFeature

    from .dut.stopwatch import StopwatchApp


    class MyAppFeature(AppFeature):

        def get_app(self):
            return StopwatchApp()


    class SetupStopwatch(balder.Setup):

        class App(balder.Device):
            app = MyAppFeature()

        @balder.connect(App, over_connection=balder.Connection)
        class Controller(balder.Device):
            textual = TextualControlFeature(App="App")

With this setup, Balder can launch your Textual app in a controlled environment for testing.

As this package does not provide any test scenarios by itself, you need to define one.

Adding Pages and Widgets
========================

To test specific parts of your app (like screens or widgets), BalderHub lets you define "pages" that map to UI elements.
A ``TextualPage`` represents a view in your app and provides properties for easy access to widgets.

Create a new file for pages (e.g., ``pages.py``).

Here's how to define a page for a stopwatch:

* Import additional utilities from BalderHub for pages, components, and selectors.
* Define a TextualPage subclass with properties for each widget you want to interact with.
* Use selectors to locate widgets by tag, ID, or other attributes.


.. code-block:: python

    # file: pages.py

    from balderhub.textual.lib.scenario_features import TextualPage
    from balderhub.textual.lib.utils import components
    from balderhub.textual.lib.utils.selector import Selector

    class StopwatchPage(TextualPage):
        """
        This page represents the stopwatch screen in your Textual app.
        It defines properties for key widgets like the time display and buttons.
        """

        @property
        def numbers(self) -> components.widgets.Digits:
            """
            Returns the time display widget.
            Assumes it's a Digits widget with a tag 'TimeDisplay'.
            """
            return components.widgets.Digits.by_selector(self.driver, Selector.by_tag('TimeDisplay'))

        @property
        def btn_start(self) -> components.widgets.Button:
            """
            Returns the 'Start' button by its ID.
            """
            return components.widgets.Button.by_selector(self.driver, Selector.by_id('start'))

        @property
        def btn_stop(self) -> components.widgets.Button:
            """
            Returns the 'Stop' button by its ID.
            """
            return components.widgets.Button.by_selector(self.driver, Selector.by_id('stop'))

        @property
        def btn_reset(self) -> components.widgets.Button:
            """
            Returns the 'Reset' button by its ID.
            """
            return components.widgets.Button.by_selector(self.driver, Selector.by_id('reset'))

Using the :class:`TextualPage` allows to define widgets according to the Page-Object-Model. Within this class there are
three main key concepts used here:

* ``TextualPage``: A base class from BalderHub that gives you a driver to interact with the app's UI.
* Properties: These are like getters for widgets. Use by_selector to find them dynamically.
* Selectors: Tools like Selector.by_id or Selector.by_tag help locate elements without hardcoding paths. This makes your tests more robust if the UI changes slightly.

Writing a Test Scenario
=======================

Now, let's use our page directly within a Balder scenario and add a new test to it.

.. code-block:: python

    # file scenario_stopwatch.py
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

            displayed_time = datetime.time.fromisoformat(self.Controller.page.numbers.text)

            displayed_sec = displayed_time.second + displayed_time.microsecond / 1_000_000

            assert displayed_time.hour == 0
            assert displayed_time.minute == 0
            # we are using this high deviation because of performance issues in Textual Pilot
            assert math.isclose(displayed_sec, expected_time, rel_tol=0.5), f"wrong time displayed: {displayed_sec} instead of {expected_time}"


That's it.

**Breaking It Down:**

* ``ScenarioStoppTime``: Inherits from balder.Scenario. Define devices here (like Controller with the page).
* ``test_start_stop``: A test method that simulates user actions:
    * Access widgets via ``self.Controller.page.<property>``.
    * Use methods like ``.click()`` to interact.
    * Read values with ``.text`` and assert them.
* Assertions: We use ``math.isclose`` for floating-point comparison since timings might not be exact.
* ``time.sleep``: This pauses the test to simulate time passing. In real tests, consider using more precise timing if needed.

Running Balder
==============

Before we can run Balder, we need to add the page to the setup too. Open the existing file ``setup_stopwatch.py`` and
add the page to the existing device ``Controller``:

.. code-block:: python

    # file `setup_stopwatch.py`

    ...

    from .dut.stopwatch import StopwatchApp


    ...

    class SetupStopwatch(balder.Setup):
        class App(balder.Device):
            app = MyAppFeature()

        @balder.connect(App, over_connection=balder.Connection)
        class Controller(balder.Device):
            textual = TextualControlFeature(App="App")
            page = StopwatchPage()

To run this, ensure your setup file is imported or discoverable, then execute balder:


.. code-block:: shell

    $ balder


The test will be executed. You should see something similar to the shown output below:

.. code-block:: shell

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.12 (main, Dec 30 2025, 03:58:12) [GCC 14.2.0] | balder version 0.1.0                            |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupStopwatch
      SCENARIO ScenarioStopWatch
        VARIATION ScenarioStopWatch.App:SetupStopwatch.App | ScenarioStopWatch.Controller:SetupStopwatch.Controller
          TEST ScenarioStopWatch.test_start_stop [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
