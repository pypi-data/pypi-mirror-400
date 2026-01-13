import abc
import functools

from .factory import FactoryCoreBase


def to_subfactory(method):
    """Decorator for MultiFactory _from_json* methods

    Decorated method should only provide the correct key to select the factory from MultiFactory.factories. This
    decorator will then instantiate a factory instance and call the subclass _from_json* method with the same name.

    Parameters
    ----------
    method : callable
        _from_json* method on MultiFactory

    Returns
    -------
    callable
        Method that instantiates a TrendMiner object of the correct class
    """
    @functools.wraps(method)
    def inner(*args, **kwargs):
        """Inner function that creates a factory instance and calls the _from_json* method"""
        factory = args[0]._subfactory(method(*args, **kwargs))
        return getattr(factory, method.__name__)(*args[1:], **kwargs)

    return inner


class MultiFactoryBase(FactoryCoreBase, abc.ABC):
    """Base factory for when multiple class types are allowed for the same attribute"""
    factories = {}

    @classmethod
    def _correct_class(cls, ref):
        """Checks if an input is already of one of the supported classes"""
        return any(factory._correct_class(ref) for factory in cls.factories.values())

    def _subfactory(self, key):
        """Return subfactory instance from key

        Parameters
        ----------
        key : str
            key to self.factories dict

        Returns
        -------
        Any
            Subfactory instance
        """
        return self.factories[key](client=self.client)
