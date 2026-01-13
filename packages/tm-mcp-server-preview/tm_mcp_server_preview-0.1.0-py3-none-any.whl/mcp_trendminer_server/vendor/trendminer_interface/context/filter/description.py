from trendminer_interface import _input as ip
from trendminer_interface.base import FactoryBase
from trendminer_interface.context.filter.base import ContextFilterWithModeBase


class DescriptionFilter(ContextFilterWithModeBase):
    """Filter on context item description"""
    filter_type = "DESCRIPTION_FILTER"

    def __init__(self, client, values, mode):
        super().__init__(client=client, mode=mode)
        self.values = values

    @property
    def values(self):
        """Filter values

        Returns
        -------
        values : list of str
            String queries to filter on the description
        """
        return self._values

    @values.setter
    def values(self, values):
        self._values = ip.any_list(values)

    def _json(self):
        return {
            **super()._json(),
            "values": self.values,
        }


class DescriptionFilterFactory(FactoryBase):
    """Factory for context item description filter creation"""
    tm_class = DescriptionFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        DescriptionFilterFactory
        """
        return self.tm_class(client=self.client, values=data.get("values"), mode=data.get("mode"))

    def __call__(self, values=None, mode=None):
        """Create new description context filter

        Parameters
        ----------
        values : list of str, optional
            Values on which to filter the description. Can take '*' as wildcard character.
        mode : str, optional
            Filter for "EMPTY" or "NON_EMPTY" description. When using mode, any given values are ignored.

        Returns
        -------
        DescriptionFilter
            Filter on context item description
        """
        return self.tm_class(client=self.client, values=values, mode=mode)
