from trendminer_interface.base import SerializableBase, FactoryBase, ByFactory, HasOptions
from trendminer_interface.component_factory import ComponentMultiFactory
from trendminer_interface.constants import ASSET_INCLUDE_OPTIONS
from trendminer_interface.asset import Asset, Attribute


class ComponentQuery(SerializableBase):
    """Query for filtering components in component context filter

    Attributes
    ----------
    component : Tag or Attribute or Asset
        Underlying component
    include : str, optional
        "SELF", "ANCESTORS" or "DESCENDANTS". Only applicable to assets and attributes. Descendants only possible for
        assets.
    """
    component = ByFactory(ComponentMultiFactory)
    include = HasOptions(ASSET_INCLUDE_OPTIONS)

    def __init__(self, client, component, include):
        super().__init__(client=client)
        self.component = component
        self.include = include

    def _json(self):
        if isinstance(self.component, (Asset, Attribute)):
            node_payload = {
                "include": self.include or "SELF",
                "path": self.component.path_hex
            }
        else:
            node_payload = {}

        return {
            "type": self.component.component_type,
            "identifier": self.component.identifier,
            **node_payload,
        }


class ComponentQueryFactory(FactoryBase):
    """Factory for creating component queries"""
    tm_class = ComponentQuery

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ComponentQuery
        """
        return self.tm_class(
            client=self.client,
            component=ComponentMultiFactory(client=self.client)._from_json_context_item(data),
            include=data.get('include'),
        )

    def from_query(self, query):
        """Convert input to ComponentQuery

        Parameters
        ----------
        query : Any
            Either single (reference to) component, or tuple with as first value the component and then whether
            ancestors or descendants need to be included ("SELF", "ANCESTORS", or "DESCENDANTS").
        """
        if isinstance(query, tuple):
            try:
                include = query[1]
            except IndexError:
                include = None
            return self.tm_class(client=self.client, component=query[0], include=include)

        return self.tm_class(client=self.client, component=query, include=None)

    @property
    def _get_methods(self):
        return self.from_query,
