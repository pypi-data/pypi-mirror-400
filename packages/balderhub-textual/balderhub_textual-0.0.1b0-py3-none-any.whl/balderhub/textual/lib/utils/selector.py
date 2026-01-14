from enum import Enum

from balderhub.gui.lib.utils.base_selector import BaseSelector


class Selector(BaseSelector):
    """specific textual selector class"""

    class By(Enum):
        """
        Enum that describes the selecting type
        """
        ID = 'id'
        CLASSNAME = 'class name'
        TAG = "tag name"

    @classmethod
    def by_id(cls, name: str):
        """creates a new selector identified by the id"""
        return cls(cls.By.ID, name)

    @classmethod
    def by_tag(cls, name: str):
        """creates a new selector identified by the tag name"""
        return cls(cls.By.TAG, name)

    @classmethod
    def by_class(cls, name: str):
        """creates a new selector identified by a class name"""
        return cls(cls.By.CLASSNAME, name)

    def to_textual_string(self):
        """
        Converts the selector into the textual notation
        """
        if self._by_type == self.By.ID:
            return f'#{self._identifier}'
        if self._by_type == self.By.CLASSNAME:
            return f'.{self._identifier}'
        if self._by_type == self.By.TAG:
            return f'{self._identifier}'
        raise KeyError(f"Unknown selector type: {self._by_type}")
