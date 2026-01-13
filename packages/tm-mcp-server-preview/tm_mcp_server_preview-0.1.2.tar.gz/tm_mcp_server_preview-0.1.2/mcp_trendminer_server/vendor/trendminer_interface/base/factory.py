import abc
import functools

from collections.abc import MutableMapping
from requests.exceptions import HTTPError

from trendminer_interface import _input as ip
from trendminer_interface.exceptions import ResourceNotFound
from .lazy_loading import LazyAttribute
from .objects import AuthenticatableBase


class FactoryCoreBase(AuthenticatableBase, abc.ABC):
    """Superclass for all factories instantiating new methods"""

    @property
    def _get_methods(self):
        """Methods to try to retrieve an instance from the appliance

        get methods always have the following syntax: `from_*`
        """
        return ()

    @classmethod
    @abc.abstractmethod
    def _correct_class(cls, ref):
        """Check if input is already of the correct class"""
        pass

    def _get(self, ref):
        """Get instance from any possible reference type

        Tries all methods in `_get_methods` in order to retrieve an instance from the appliance.

        The given input is simply returned if:
        - It is already an instance of the correct type
        - It is None
        - It is a LazyAttribute

        Parameters
        ----------
        ref : Any
            Reference by which a unique instance can be retrieved from the appliance

        Returns
        -------
        Any
            The instance pointed to by the given reference
        """

        if ref is None:
            return None

        if isinstance(ref, LazyAttribute):
            return ref

        # Ref is already of correct instance, return
        if self._correct_class(ref):
            return ref

        # Try all other implemented methods to return data
        for method in self._get_methods:
            try:
                return method(ref)
            except (ResourceNotFound, AttributeError, TypeError, ValueError):
                pass
            except HTTPError as err:
                if err.response.status_code not in [400, 404]:
                    raise err

        raise ResourceNotFound(f"No match for {ref} found")

    def _list(self, refs):
        """Retrieves instances from list of references

        Uses the `get` method on every item in the given list.

        Parameters
        ----------
        refs : list or Any
            list of references representing unique instances on the appliance. A single input is converted into a list
            of length 1.

        Returns
        -------
        list
            List of instances retrieved from given references
        """
        if isinstance(refs, LazyAttribute):
            return refs
        if refs is None:
            refs = []
        if isinstance(refs, (str, tuple, MutableMapping)) or self._correct_class(refs):
            refs = [refs]
        return [self._get(ref) for ref in refs]

    def _cache_key_ref(self, ref=None):
        """Cachetools key for methods with ref argument or without arguments

        Caching factory methods conventionally has no effect as new factory classes are created on the fly. The cache
        key for a method is thus set based on the client (as well as the input, of course). This key function can be
        used for caching methods where ref is the only input.

        Cache decorator should follow this syntax:
        `@cachetools.cached(..., key=TrendMinerFactory._cache_key_ref)`

        Parameters
        ----------
        ref : Any, optional
            Input to the cached method

        Returns
        -------
        key: tuple
            Cache key
        """

        # Handling for object inputs
        if isinstance(ref, AuthenticatableBase):
            ref = hash(ref)

        key = hash(self.client), ref

        return key


class FactoryBase(FactoryCoreBase, abc.ABC):
    """Superclass for all factories instantiating new methods"""
    tm_class = abc.abstractmethod(lambda: None)

    @property
    def _endpoint(self):
        # TODO: remove endpoint concept. It does not universally apply. Just putting the url when doing the request is clearer.
        return self.tm_class.endpoint

    @classmethod
    def _correct_class(cls, ref):
        """Check if input is already of the correct class"""
        return isinstance(ref, cls.tm_class)


def kwargs_to_class(method):
    """Decorator function that handles turning keyword arguments into a TrendMiner class instance

    Intended to decorate _from_json* methods on TrendMiner Factory classes. Creates an instance in which attributes not
    provided through the output dict are turned into LazyAttribute instances. This shortens our code as we no longer
    explicitly need to set our lazy attributes. Also allows the addition of a `from_list` parameter which will iterate
    the base method to turn a list of inputs into a list of instances. Prevents us from having to use list comprehension
    in our methods.

    Parameters
    ----------
    method : callable
        Method turning json input into a dict of kwargs usable for creating a class instances

    Returns
    -------
    callable
    """

    @functools.wraps(method)
    def inner(*args, **kwargs):
        """Decorator inner function. Creates a class instance or list of class instances."""

        self = args[0]
        try:
            data = args[1]
        except IndexError:
            data = kwargs["data"]

        values = method(self, data)

        output = {
            kw: LazyAttribute(name=kw)
            for kw in self.tm_class.__init__.__code__.co_varnames
        }
        output.pop("self")
        output.update({"client": self.client, **values})
        return self.tm_class(**output)
    return inner
