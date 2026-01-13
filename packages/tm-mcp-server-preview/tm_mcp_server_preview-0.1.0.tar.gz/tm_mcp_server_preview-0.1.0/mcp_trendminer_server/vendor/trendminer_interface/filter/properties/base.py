import abc
from trendminer_interface.base import SerializableBase


class FilterPropertiesBase(SerializableBase, abc.ABC):
    """Abstract base class for filter properties"""
    properties_type = abc.abstractmethod(lambda: None)

    @abc.abstractmethod
    def _json_properties(self):
        pass

    def _json(self):
        return {
            "properties": self._json_properties(),
            "type": self.properties_type,
        }
