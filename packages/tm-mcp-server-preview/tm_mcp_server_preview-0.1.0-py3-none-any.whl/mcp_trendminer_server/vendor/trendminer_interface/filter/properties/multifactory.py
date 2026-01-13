from trendminer_interface.base import MultiFactoryBase, to_subfactory
from .manual import ManualFilterPropertiesFactory
from .search import SearchFilterPropertiesFactory


class FilterPropertiesMultiFactory(MultiFactoryBase):
    """MultiFactory for retrieving any filter properties"""
    factories = {
        factory.tm_class.properties_type: factory
        for factory in [ManualFilterPropertiesFactory, SearchFilterPropertiesFactory]
    }

    @to_subfactory
    def _from_json(self, data):
        return data["type"]
