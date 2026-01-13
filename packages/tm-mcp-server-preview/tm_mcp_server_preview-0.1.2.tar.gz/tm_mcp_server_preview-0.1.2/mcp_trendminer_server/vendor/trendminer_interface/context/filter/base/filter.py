import abc
from trendminer_interface.base import SerializableBase


class ContextFilterBase(SerializableBase, abc.ABC):
    """The basis of a context filter: can be constructed from and returned to json format, and made new by the user"""
    filter_type = abc.abstractmethod(lambda: None)

    def _json(self):
        return {"type": self.filter_type}

    def __repr__(self):
        return f"<< {self.__class__.__name__} >>"