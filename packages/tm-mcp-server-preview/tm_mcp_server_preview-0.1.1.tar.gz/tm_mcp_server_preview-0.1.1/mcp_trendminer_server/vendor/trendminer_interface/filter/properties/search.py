from trendminer_interface.search import SearchMultiFactory
from trendminer_interface.base import ByFactory, FactoryBase

from .base import FilterPropertiesBase


class SearchFilterProperties(FilterPropertiesBase):
    """Filter properties for a filter derived from a search

    Attributes
    ----------
    search: Any
        The search the filter is derived from
    filter_results : bool
        When True, search results are filtered out. Otherwise, everything that is not a search result will be filtered
        out.
    """

    properties_type = "SEARCH_BASED"
    search = ByFactory(SearchMultiFactory)

    def __init__(self, client, search, filter_results):
        super().__init__(client=client)
        self.search = search
        self.filter_results = filter_results

    def _json_properties(self):
        return {
            "searchIdentifier": self.search.identifier_complex,
            "searchIncluded": self.filter_results,
            "searchMetaData": {
                "description": self.search.description,
                "name": self.search.name,
                "type": self.search.content_type,
            }
        }


class SearchFilterPropertiesFactory(FactoryBase):
    """Factory for retrieving search-derived filter properties"""
    tm_class = SearchFilterProperties

    def _from_json(self, data):
        return self.tm_class(
            client=self.client,
            search=SearchMultiFactory(client=self.client)._from_json_filter(data),
            filter_results=data["properties"]["searchIncluded"]
        )
