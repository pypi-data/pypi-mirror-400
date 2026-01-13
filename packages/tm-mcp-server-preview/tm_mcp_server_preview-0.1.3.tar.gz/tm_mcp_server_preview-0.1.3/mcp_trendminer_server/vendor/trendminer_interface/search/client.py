import abc

from trendminer_interface.fingerprint import FingerprintSearchFactory
from trendminer_interface.base import to_subfactory
from trendminer_interface.work import WorkOrganizerObjectMultiFactoryBase

from .value import ValueBasedSearchFactory
from .similarity import SimilaritySearchFactory


class SearchClient(abc.ABC):
    """Search client"""
    @property
    def search(self):
        """Parent factory for all search types"""
        return SearchMultiFactory(client=self)


search_factories = {
        factory.tm_class.content_type: factory
        for factory in [
            ValueBasedSearchFactory,
            SimilaritySearchFactory,
        ]
    }

# Conversion dict for monitor search type (e.g. valuebased) to work organizer content type (e.g. VALUE_BASED_SEARCH)
search_type_to_content_type = {
    factory.tm_class.search_type: content_type
    for content_type, factory in search_factories.items()
}


class SearchMultiFactory(WorkOrganizerObjectMultiFactoryBase):
    """Parent factory for all search types"""

    endpoint = "/work/saveditem/"
    factories = search_factories

    @property
    def value(self):
        """Factory for value-based searches

        Returns
        -------
        ValueBasedSearchFactory
        """
        return ValueBasedSearchFactory(client=self.client)

    @property
    def similarity(self):
        """Factory for similarity searches

        Returns
        -------
        SimilaritySearchFactory
        """
        return SimilaritySearchFactory(client=self.client)

    @property
    def fingerprint(self):
        """Factory for fingerprint searches

        Fingerprint searches are not work organizer objects and cannot be saved. They can only be instantiated and
        executed. Their signature is not the same as those of other searches.

        Returns
        -------
        FingerprintSearchFactory
        """
        return FingerprintSearchFactory(client=self.client)

    @to_subfactory
    def _from_json_monitor(self, data):
        return search_type_to_content_type[data["type"]]

    @to_subfactory
    def _from_json_monitor_all(self, data):
        return search_type_to_content_type[data["type"]]

    @to_subfactory
    def _from_json_monitor_nameless(self, data):
        return search_type_to_content_type[data["type"]]

    @to_subfactory
    def _from_json(self, data):
        return data["type"]

    @to_subfactory
    def _from_json_filter(self, data):
        return data["properties"]["searchMetaData"]["type"]

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_path, self.from_name
