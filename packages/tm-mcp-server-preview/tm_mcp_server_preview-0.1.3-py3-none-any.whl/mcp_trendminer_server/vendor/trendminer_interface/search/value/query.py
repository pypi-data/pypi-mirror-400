import re
from trendminer_interface import _input as ip
from trendminer_interface.constants import VALUE_BASED_SEARCH_OPERATORS
from trendminer_interface.base import FactoryBase, HasOptions
from trendminer_interface.search.tag import ReferencingTagBase, TagFactory


class SearchQuery(ReferencingTagBase):
    condition = HasOptions(VALUE_BASED_SEARCH_OPERATORS)

    def __init__(self, client, tag, condition, values):
        super().__init__(client=client, tag=tag)
        self.condition = condition
        self.values = values

    @property
    def values(self):
        if self.tag.numeric:
            return [float(value) for value in ip.any_list(self._values)]
        else:
            # return strings to the user for non-numeric tags
            return [self.tag.states[i] for i in self._values]

    @property
    def values_numeric(self):
        if self.tag.numeric:
            return [float(value) for value in ip.any_list(self._values)]
        return self._values

    @values.setter
    def values(self, values):
        # json input, avoid request to load tag data
        if "_tag_type" in self.tag.lazy:
            self._values = values
        # user input, process
        else:
            values = ip.any_list(values)
            if self.condition.lower() == "constant":
                values = []
            if self.tag.numeric:
                # converting numeric values to floats
                self._values = [float(value) for value in values]
            else:
                # convert to state indices for non-numeric tags
                self._values = [state if isinstance(state, int) else self.tag._get_state_index(state) for state in values]

    def _json(self):
        return {
            **super()._json(),
            "condition": self.condition,
            "values": self.values_numeric,
        }

    def __repr__(self):
        if self.condition == "Constant":
            value_str = ""
        else:
            value_str = f" {self.values}"
        return f'<< {self.__class__.__name__} | {self.tag.name} {self.condition}{value_str} >>'


class SearchQueryFactory(FactoryBase):
    tm_class = SearchQuery

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        SearchQuery
        """
        operator = data["operator"]
        values = data["value"]
        if operator == "Constant":
            values = []
        return self.tm_class(
            client=self.client,
            tag=TagFactory(client=self.client)._from_json_search_query(data),
            condition=data["operator"],
            values=values,
        )

    def from_query(self, query):
        if isinstance(query, str):
            condition = re.search("([<>=!]{1,2}[ ]*)|(constant[ ]*$)", query, re.IGNORECASE).group().strip().lower()
            (tag, value) = [part.strip() for part in query.split(condition)]
            values = [value]

        elif isinstance(query, dict):
            tag = query["reference"]
            condition = query["operator"]
            values = query["values"]

        else:
            tag = query[0]
            condition = query[1]
            try:
                values = ip.any_list(query[2])
            except IndexError:
                values = None

        return SearchQuery(
            client=self.client,
            tag=tag,
            condition=condition,
            values=values,
        )

    @property
    def _get_methods(self):
        return self.from_query,