from trendminer_interface.constants import SEARCH_CALCULATION_OPTIONS
from trendminer_interface.base import FactoryBase, HasOptions
from .tag import ReferencingTagBase, TagFactory


class SearchCalculation(ReferencingTagBase):
    """Calculation on search results

    Attributes
    ----------
    operation : str
        MEAN, MIN, MAX, RANGE, START, END, DELTA, INTEGRAL or STDEV
    key : str
        Calculation reference key.
    units : str
        Calculation units
    """
    operation = HasOptions(SEARCH_CALCULATION_OPTIONS)

    def __init__(
            self,
            client,
            key,
            tag,
            operation,
            units,
    ):
        super().__init__(client=client, tag=tag)

        self.operation = operation
        self.key = key
        self.units = units

    def _json(self):
        return {
            **super()._json(),
            "name": self.key,
            "type": self.operation,
            "unit": self.units,
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.tag.name} | {self.operation} >>"


class SearchCalculationFactory(FactoryBase):
    """Factory class for creating search calculation objects"""
    tm_class = SearchCalculation

    def __call__(self, tag, operation, key=None, units=""):
        return self.tm_class(
            client=self.client,
            tag=tag,
            operation=operation,
            key=key,
            units=units,
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        SearchCalculation
        """
        return self.tm_class(
            client=self.client,
            tag=TagFactory(client=self.client)._from_json_calculation(data["reference"]),
            operation=data["type"],
            key=data["name"],
            units=data["unit"],
        )

    def from_dict(self, refs):
        """Create list of search calculations from a dict

        Dict keys are calculation keys. Values are `(tag, operation, unit)` tuples, where the unit entry is optional.

        Parameters
        ----------
        refs : dict
            Dictionary of calculations

        Returns
        -------
        list of SearchCalculation

        Examples
        --------
        ```
        from_dict(
            {
                'max flow': (flow_tag, 'MAX', 'm3/h'),
            }
        )
        ```
        """

        calculations = []
        for key, value in refs.items():
            tag = value[0]
            operation = value[1]
            try:
                units = value[2]
            except IndexError:
                units = ""
            calculations.append(
                self.tm_class(
                    client=self.client,
                    tag=tag,
                    operation=operation,
                    key=key,
                    units=units,
                )
            )
        return calculations

    def _list(self, refs):
        """Extends TrendMinerFactory._list to account for `from_dict` method

        Attributes
        ----------
        refs : list or dict or Any
            References to be converted to search calculations

        Returns
        -------
        list of SearchCalculation
        """
        try:
            return self.from_dict(refs)
        except AttributeError:
            return super()._list(refs)

    @property
    def _get_methods(self):
        return ()