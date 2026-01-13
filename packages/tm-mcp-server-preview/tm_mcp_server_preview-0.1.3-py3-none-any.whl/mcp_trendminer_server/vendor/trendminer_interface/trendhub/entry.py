from trendminer_interface.base import MultiFactoryBase, to_subfactory
from .group import TrendHubEntryGroupFactory
from .data_reference_factory import DataReferenceMultiFactory


class TrendHubEntryMultiFactory(MultiFactoryBase):
    """Factory for generating TrendHub view entries

    TrendHub view entries can be tags, attributes, and groups of tags and/or attributes
    """
    factories = {
        "DATA_REFERENCE": DataReferenceMultiFactory,
        "GROUP": TrendHubEntryGroupFactory,
    }

    @to_subfactory
    def _from_json_trendhub(self, data):
        return data["type"]

    @property
    def _get_methods(self):
        return self._subfactory("DATA_REFERENCE")._get_methods
