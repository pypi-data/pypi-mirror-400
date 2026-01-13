from trendminer_interface.base import MultiFactoryBase, to_subfactory, ComponentFactoryMixin
from trendminer_interface.tag import TagFactory
from trendminer_interface.asset import AttributeFactory, AssetFactory, NodeMultiFactory


class ComponentMultiFactory(MultiFactoryBase, ComponentFactoryMixin):
    """Factory for retrieving ContextHub components"""
    factories = {
        "TAG": TagFactory,
        "ASSET": AssetFactory,
        "ATTRIBUTE": AttributeFactory,
    }

    @property
    def _get_methods(self):
        return (
            self._subfactory("TAG").from_identifier,
            NodeMultiFactory(client=self.client).from_identifier,
            self._subfactory("TAG").from_name,
            NodeMultiFactory(client=self.client).from_path_hex,
            NodeMultiFactory(client=self.client).from_path,
        )

    @to_subfactory
    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data["type"]

    @to_subfactory
    def _from_json_context_item(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data["type"]

    # TODO: this is not a ComponentFactory method, since it does not work for assets!
    @to_subfactory
    def _from_json_current_value_tile(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data["type"]
