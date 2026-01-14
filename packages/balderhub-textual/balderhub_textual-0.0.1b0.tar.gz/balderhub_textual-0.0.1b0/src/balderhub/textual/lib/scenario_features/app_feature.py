import textual.app
from balder import Feature


class AppFeature(Feature):
    """
    Basic feature that provides the textual app instance that should be tested.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._async_pilot_cm = None
        self._pilot_instance = None

    def get_app(self) -> textual.app.App:
        """
        Returns the app instance that should be tested.
        """
        raise NotImplementedError()
