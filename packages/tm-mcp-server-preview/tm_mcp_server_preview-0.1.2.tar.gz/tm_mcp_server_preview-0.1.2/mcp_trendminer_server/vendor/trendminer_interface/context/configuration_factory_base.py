import abc
import posixpath

from trendminer_interface.base import FactoryBase
from trendminer_interface.constants import MAX_GET_SIZE


# TODO: too much complexity for little added value -> remove
class ContextConfigurationFactoryMixin(FactoryBase, abc.ABC):
    """Mixin class for context configuration class factories

    Factories for
    - Context workflow
    - Context field
    - Context type

    Implements sql-style query searching and some base retrieval methods
    """

    @abc.abstractmethod
    def _from_json(self, data):
        pass

    def from_identifier(self, ref):
        """Retrieve instances from its identifier

        Parameters
        ----------
        ref : str
            Instance UUID

        Returns
        -------
        Any
            Instance with the given UUI
        """
        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)
        return self._from_json(response.json())

    @abc.abstractmethod
    def search(self, **kwargs):
        pass

    def all(self):
        """Retrieve all instances

        Returns
        -------
        list
            List of all instances the user has access to
        """
        return self.search("*")