from trendminer_interface.base import ByFactory, FactoryBase
from trendminer_interface.context.filter.base import ContextFilterWithModeBase
from .query import ComponentQueryFactory


class ComponentFilter(ContextFilterWithModeBase):
    """Filter on set of components

    Components can be tags, attributes or assets.

    Attributes
    ----------
    component_queries : list of ComponentQuery
        Component queries on which to filter. Component queries contain the component, but also whether ancestors or
        children need to be included
    """
    filter_type = "COMPONENT_FILTER"
    component_queries = ByFactory(ComponentQueryFactory, "_list")

    def __init__(self, client, components, mode):
        super().__init__(client=client, mode=mode)
        self.component_queries = components

    def _json(self):
        return {
            **super()._json(),
            "components": [query._json() for query in self.component_queries],
        }


class ComponentFilterFactory(FactoryBase):
    """Factory for generating component filters"""
    tm_class = ComponentFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ComponentFilter
        """
        return self.tm_class(
            client=self.client,
            components=[
                ComponentQueryFactory(client=self.client)._from_json(component)
                for component in data.get("componentResources", [])
            ],
            mode=data.get("mode")
        )

    def __call__(self, components=None, mode=None):
        """Create a new component filter

        Parameters
        ----------
        components : list
            List of (references to) components on which to filter. If ancestors (for assets and attributes) or
            descendants (for assets) need to be included, provide list entries as tuples like this:
            (MyAsset, "DESCENDANTS"), (MyAttribute, "ANCESTORS").
        mode : str, optional
            Filter for "EMPTY" or "NON_EMPTY" component attribute. When using mode, any given components are ignored.

        Returns
        -------
        ComponentFilter
            Filter on context item components
        """
        return self.tm_class(
            client=self.client,
            components=components,
            mode=mode,
        )
