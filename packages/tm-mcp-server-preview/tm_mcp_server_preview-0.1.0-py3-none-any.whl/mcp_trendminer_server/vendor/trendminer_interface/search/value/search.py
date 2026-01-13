import pandas as pd

from trendminer_interface.base import ByFactory, HasOptions, kwargs_to_class, AsTimedelta
from trendminer_interface.search.base import SearchBase, SearchFactoryBase
from trendminer_interface.search.calculation import SearchCalculationFactory

from .query import SearchQueryFactory


class ValueBasedSearch(SearchBase):
    content_type = "VALUE_BASED_SEARCH"
    search_type = "valuebased"

    queries = ByFactory(SearchQueryFactory, "_list")
    duration = AsTimedelta()
    operator = HasOptions(["AND", "OR"])

    def __init__(self,
                 client,
                 identifier,
                 identifier_complex,
                 name,
                 description,
                 parent,
                 owner,
                 last_modified,
                 version,
                 queries,
                 calculations,
                 duration,
                 operator,
                 ):
        super().__init__(
            client=client,
            identifier=identifier,
            name=name,
            description=description,
            parent=parent,
            owner=owner,
            last_modified=last_modified,
            version=version,
            calculations=calculations,
            identifier_complex=identifier_complex,
        )

        self.queries = queries
        self.duration = duration
        self.operator = operator

    @property
    def tags(self):
        return [query.tag for query in self.queries]

    def _json_definition(self):
        return {
            **super()._json_definition(),
            "queries": [query._json() for query in self.queries],
            "parameters": {
                "minimumDuration": int(self.duration.total_seconds()),
                "operator": self.operator,
            },
        }

    def _json_data_queries(self):
        query_data = []

        for query in self.queries:
            value = query.values_numeric
            operator = query.condition
            if operator.lower() == "constant":
                value = ""
            elif query.tag.numeric:
                value = value[0]
                if value == int(value):
                    value = int(value) # converting to int when possible avoids phantom 'unsaved changes' in ux
                value = str(value)
            elif operator == "=":
                operator = "In set"

            query_data.append(
                {
                    "interpolationType": query.tag._interpolation_payload_str_lower,
                    "operator": operator,
                    "shift": int(query.tag.shift.total_seconds()),
                    "tagName": query.tag.name,
                    "value": value
                }
            )

        return query_data

    def _json_data(self):
        return {
            "calculations": [calculation._json() for calculation in self.calculations],
            "minimumIntervalLength": str(int(self.duration.total_seconds())),
            "operator": self.operator,
            "queries": self._json_data_queries(),
        }


class ValueBasedSearchFactory(SearchFactoryBase):
    tm_class = ValueBasedSearch

    def __call__(
            self,
            queries,
            name="New Search",
            description="",
            parent=None,
            duration=None,
            calculations=None,
            operator="AND",
    ):
        duration = duration or 2*self.client.resolution

        return self.tm_class(
            client=self.client,
            identifier=None,
            identifier_complex=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            queries=queries,
            duration=duration,
            calculations=calculations,
            operator=operator,
        )

    def _json_data(self, data):
        return {
            "identifier_complex": data["data"]["id"],
            "calculations": [
                SearchCalculationFactory(client=self.client)._from_json(calc) for calc in data["data"]["calculations"]
            ],
            "duration": pd.Timedelta(seconds=float(data["data"]["minimumIntervalLength"])),  # given as string
            "operator": data["data"]["operator"],
            "queries": [
                SearchQueryFactory(client=self.client)._from_json(query)
                for query in data["data"]["queries"]
                ],
        }
