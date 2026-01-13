from trendminer_interface.base import MultiFactoryBase, to_subfactory
from trendminer_interface.asset import AttributeFactory
from trendminer_interface.tag import TagFactory


class DataReferenceMultiFactory(MultiFactoryBase):
    """Factory for creating and retrieving tags and attributes"""
    factories = {
        "TIME_SERIES": TagFactory,
        "ATTRIBUTE": AttributeFactory,
    }

    @property
    def _get_methods(self):
        return (
            self._subfactory("TIME_SERIES").from_identifier,
            self._subfactory("ATTRIBUTE").from_identifier,
            self._subfactory("ATTRIBUTE").from_path_hex,
            self._subfactory("TIME_SERIES").from_name,
            self._subfactory("ATTRIBUTE").from_path,
        )

    @to_subfactory
    def _from_json_trendhub(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data["dataReference"]["type"]

    @to_subfactory
    def _from_json_trendhub_group(self, data):
        return data["type"]
